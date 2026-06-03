"""monitor — guardião read-only da Malto Maia.

Checks determinísticos que o agente .claude/agents/monitor.md roda pra
"ficar de olho" no que mexemos. NÃO edita NADA. Só observa e reporta.

Uso:
    python scripts/dev/monitor.py                 # roda todos, relatório texto
    python scripts/dev/monitor.py --json          # saída JSON (pro agente consumir)
    python scripts/dev/monitor.py --only auth,i18n
    python scripts/dev/monitor.py --skip django   # pula um check lento

Checks (severidade entre parênteses):
    django      (alto)  manage.py check — erros de deploy/config
    migrations  (alto)  makemigrations --check — model mudou sem migration
    auth        (medio) view do painel sem @staff_required fora da allowlist pública
    secrets     (alto)  segredo hardcoded fora de env
    i18n        (medio) string de UI sem PT ou EN em core/i18n.py
    static      (info)  static/ mudou — lembrar de collectstatic/redeploy

Heurísticas geram FALSO POSITIVO de propósito — é um vigia, não um juiz.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SETTINGS = "maltomaia.settings.dev"

_APPS = ["core", "cardapio", "pedidos", "painel"]

# Views que SÃO públicas por design — não exigir login.
_PUBLIC_VIEWS = {
    "landing", "menu", "encomenda", "set_language", "health", "robots",
    "login", "logout",
}

# Decorators que indicam proteção de acesso.
_AUTH_TOKENS = (
    "staff_required", "login_required", "staff_member_required",
    "permission_required", "user_passes_test",
)


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=str(_ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError as e:
        return 127, f"comando não encontrado: {e}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout após {timeout}s"
    except Exception as e:  # noqa: BLE001 — vigia não pode crashar
        return 1, f"erro ao rodar: {e}"


def _iter_py_files():
    skip = {".venv", "venv", "node_modules", "__pycache__", ".git",
            "migrations", "data", "staticfiles"}
    for path in _ROOT.rglob("*.py"):
        if any(part in skip for part in path.parts):
            continue
        yield path


def _finding(sev, area, msg, file="", line=0):
    return {"sev": sev, "area": area, "file": file, "line": line, "msg": msg}


# ──────────────────────────────────────────────────────────────────────
# Checks
# ──────────────────────────────────────────────────────────────────────

def check_django() -> list[dict]:
    rc, out = _run([sys.executable, "manage.py", "check", f"--settings={_SETTINGS}"])
    if rc == 0:
        return []
    tail = "\n".join(out.strip().splitlines()[-12:])
    return [_finding("alto", "django", f"manage.py check falhou (rc={rc}):\n{tail}")]


def check_migrations() -> list[dict]:
    rc, out = _run([sys.executable, "manage.py", "makemigrations",
                    "--check", "--dry-run", f"--settings={_SETTINGS}"])
    if rc == 0:
        return []
    if rc in (124, 127):
        return [_finding("baixo", "migrations", f"não consegui checar: {out.strip()[:200]}")]
    tail = "\n".join(out.strip().splitlines()[-10:])
    return [_finding("alto", "migrations",
                     f"model mudou sem migration (makemigrations --check rc={rc}):\n{tail}")]


def scan_auth() -> list[dict]:
    """View FBV do painel sem decorator de acesso (fora da allowlist) → revisar."""
    out = []
    def_rx = re.compile(r"^def\s+(\w+)\s*\(\s*request\b")
    for app in _APPS:
        vf = _ROOT / app / "views.py"
        if not vf.exists():
            continue
        try:
            lines = vf.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        rel = str(vf.relative_to(_ROOT)).replace("\\", "/")
        # Só exige login no painel (resto do site é público por design).
        if app != "painel":
            continue
        for i, line in enumerate(lines):
            m = def_rx.match(line)
            if not m:
                continue
            name = m.group(1)
            if name in _PUBLIC_VIEWS or name.startswith("_"):
                continue
            deco = " ".join(lines[max(0, i - 6):i])
            if any(tok in deco for tok in _AUTH_TOKENS):
                continue
            out.append(_finding(
                "medio", "auth",
                f"view '{name}' do painel sem @staff_required aparente — confirmar acesso",
                rel, i + 1))
    return out


def scan_secrets() -> list[dict]:
    out = []
    patterns = [
        (re.compile(r"""SECRET_KEY\s*=\s*['"][^'"]{12,}['"]"""), "SECRET_KEY literal"),
        (re.compile(r"""(AWS_SECRET_ACCESS_KEY|R2_SECRET[A-Z_]*|VAPID_PRIVATE_KEY)\s*=\s*['"][^'"]{6,}['"]"""), "credencial literal"),
        (re.compile(r"""(?i)\b(password|passwd|token|api_key)\s*=\s*['"][^'"]{8,}['"]"""), "possível segredo literal"),
    ]
    env_markers = ("env(", "os.environ", "os.getenv", "getenv", "config(")
    for path in _iter_py_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        rel = str(path.relative_to(_ROOT)).replace("\\", "/")
        for i, line in enumerate(lines, 1):
            if any(mk in line for mk in env_markers):
                continue
            if "example" in rel.lower() or "test" in rel.lower():
                continue
            for rx, label in patterns:
                if rx.search(line):
                    out.append(_finding("alto", "secrets",
                                        f"{label}: confirmar se não deveria vir de env",
                                        rel, i))
                    break
    return out


def check_i18n() -> list[dict]:
    """String de UI em core/i18n.py sem PT ou EN → revisar (UI fica incompleta)."""
    out = []
    path = _ROOT / "core" / "i18n.py"
    if not path.exists():
        return out
    try:
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("_mm_i18n", path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        strings = getattr(mod, "STRINGS", {})
    except Exception as e:
        return [_finding("baixo", "i18n", f"não consegui ler STRINGS: {e}")]
    rel = "core/i18n.py"
    for key, val in strings.items():
        if not isinstance(val, dict):
            continue
        if not val.get("pt"):
            out.append(_finding("medio", "i18n", f"'{key}' sem texto PT", rel))
        if not val.get("en"):
            out.append(_finding("medio", "i18n", f"'{key}' sem texto EN", rel))
    return out


def check_static() -> list[dict]:
    rc, out = _run(["git", "status", "--porcelain"])
    if rc != 0:
        return []
    changed = [ln[3:].strip() for ln in out.splitlines() if ln.strip()]
    static_changed = [c for c in changed if c.startswith("static/") or "/static/" in c]
    if static_changed:
        sample = ", ".join(static_changed[:3])
        return [_finding("info", "static",
                         f"static/ mudou ({sample}...) — rodar collectstatic e redeploy")]
    return []


_CHECKS = {
    "django": check_django,
    "migrations": check_migrations,
    "auth": scan_auth,
    "secrets": scan_secrets,
    "i18n": check_i18n,
    "static": check_static,
}

_SEV_ORDER = {"alto": 0, "medio": 1, "baixo": 2, "info": 3}
_SEV_LABEL = {"alto": "ALTO", "medio": "MEDIO", "baixo": "BAIXO", "info": "INFO"}


def main() -> int:
    p = argparse.ArgumentParser(prog="monitor", description="Guardião read-only da Malto Maia")
    p.add_argument("--json", action="store_true", help="Saída JSON")
    p.add_argument("--only", default="", help="Lista de checks (vírgula): auth,i18n,...")
    p.add_argument("--skip", default="", help="Checks a pular (vírgula)")
    p.add_argument("--min-sev", default="info", choices=["alto", "medio", "baixo", "info"],
                   help="Só mostra achados desta severidade pra cima")
    p.add_argument("--quiet-if-clean", action="store_true",
                   help="Não imprime nada se não houver achado (ideal pra hook de Stop)")
    args = p.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    selected = [name for name in _CHECKS
                if (not only or name in only) and name not in skip]

    findings: list[dict] = []
    errors: list[str] = []
    for name in selected:
        try:
            findings.extend(_CHECKS[name]())
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")

    findings.sort(key=lambda f: (_SEV_ORDER.get(f["sev"], 9), f["area"], f["file"], f["line"]))

    min_rank = _SEV_ORDER.get(args.min_sev, 9)
    findings = [f for f in findings if _SEV_ORDER.get(f["sev"], 9) <= min_rank]

    if args.quiet_if_clean and not findings and not errors:
        return 0

    if args.json:
        print(json.dumps({"findings": findings, "errors": errors,
                          "checks": selected}, indent=2, ensure_ascii=False))
        return 1 if any(f["sev"] == "alto" for f in findings) else 0

    print(f"=== Malto Maia Monitor — {len(findings)} achado(s) "
          f"[{', '.join(selected)}] ===")
    if not findings:
        print("Nenhum achado. Tudo limpo.")
    for f in findings:
        loc = f"  {f['file']}:{f['line']}" if f["file"] else ""
        print(f"[{_SEV_LABEL.get(f['sev'], f['sev']):5s}] {f['area']:11s} {f['msg']}{loc}")
    if errors:
        print("\nChecks que não rodaram:")
        for e in errors:
            print(f"  - {e}")
    print("\nLembrete: achados são 'revisar', não veredito. Heurística gera falso positivo.")
    return 1 if any(f["sev"] == "alto" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
