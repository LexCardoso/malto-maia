"""skill_router — roteia tarefas pra skill correta + aprende com feedback.

Porte do skill_router do imob_teams (que portou do trader_agent), adaptado pra
Malto Maia (site Django single-tenant de cardapio). Sem dependencia externa (so
stdlib) — roda com o mesmo Python do projeto.

Uso tipico (3 modos):

    # 1) Modo CLI — "qual skill pra isso?"
    python scripts/dev/skill_router.py classify "vou editar o model de item do cardapio"
    python scripts/dev/skill_router.py classify --paths cardapio/models.py "preco a definir"

    # 2) Modo service — Claude escreve em inbox, le de outbox
    python scripts/dev/skill_router.py listen
    # (Claude grava data/skill_router/inbox/<task_id>.json com {"query": "..."})

    # 3) Modo feedback — operador marca acerto/erro depois
    python scripts/dev/skill_router.py feedback <task_id> maltomaia-cardapio ok
    python scripts/dev/skill_router.py feedback <task_id> maltomaia-i18n nok

    # Bonus: stats e debug
    python scripts/dev/skill_router.py stats
    python scripts/dev/skill_router.py reindex
    python scripts/dev/skill_router.py dump-index maltomaia-cardapio

Paths (relativos ao repo root):
    .claude/skills/*/SKILL.md       — fonte das skills indexadas
    data/skill_router/inbox/*.json  — tasks pra classificar
    data/skill_router/outbox/*.json — respostas com top-K skills
    data/skill_router/feedback.jsonl — append-only, aprendizado
    data/skill_router/state.json    — cache do index (regen on demand)
    data/skill_router/STOP          — touch pra parar listener

Score = base_score + path_bonus + keyword_bonus + feedback_score
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# Console Windows cp1252 crasha ao imprimir em-dash/acentos. Reconfigura utf-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SKILLS_DIR = _ROOT / ".claude" / "skills"
_DATA_DIR = _ROOT / "data" / "skill_router"
_INBOX_DIR = _DATA_DIR / "inbox"
_OUTBOX_DIR = _DATA_DIR / "outbox"
_FEEDBACK_PATH = _DATA_DIR / "feedback.jsonl"
_INDEX_PATH = _DATA_DIR / "state.json"
_STOP_PATH = _DATA_DIR / "STOP"

for d in (_INBOX_DIR, _OUTBOX_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────
# Index — lê todas as SKILL.md e extrai signal de cada uma
# ──────────────────────────────────────────────────────────────────────

_STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "em",
    "no", "na", "nos", "nas", "para", "por", "com", "sem", "que", "se", "ou",
    "e", "mas", "como", "mais", "menos", "muito", "pouco", "ja", "ainda",
    "the", "an", "of", "in", "on", "for", "to", "from", "with", "without",
    "is", "are", "was", "were", "be", "been", "have", "has", "had", "does",
    "did", "can", "should", "will", "would", "this", "that", "these", "those",
    "ser", "ter", "fazer", "estar", "ir", "haver", "vir", "ver",
    "vou", "vai", "vamos", "fui", "foi", "tem", "tenho", "tinha",
}


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    text = text.lower()
    toks = re.findall(r"[a-z_][a-z0-9_]{2,}", text)
    return {t for t in toks if t not in _STOPWORDS}


def _extract_frontmatter(text: str) -> tuple[dict, str]:
    fm: dict = {}
    if not text.startswith("---"):
        return fm, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return fm, text
    fm_text, body = parts[1], parts[2]
    cur_key: str | None = None
    for line in fm_text.split("\n"):
        line = line.rstrip()
        if not line:
            continue
        m = re.match(r"^([a-z_][a-z0-9_]*)\s*:\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            val = m.group(2).strip()
            if val == "|" or val == ">":
                fm[cur_key] = ""
            elif val:
                fm[cur_key] = val.strip("\"'")
            else:
                fm[cur_key] = ""
        elif cur_key and line.startswith(" "):
            fm[cur_key] = (fm.get(cur_key, "") + " " + line.strip()).strip()
    return fm, body


# Padrões de path/keyword que cada skill "sinaliza" — heurística manual.
_PATH_HINTS: dict[str, list[str]] = {
    # ── Meta / infra ──
    "maltomaia-skill-router": [
        "skill_router", "scripts/dev/skill_router.py", "classify", "reindex",
        "roteador", "qual skill",
    ],
    "maltomaia-memory-keeper": [
        "MEMORY.md", "memory/", "archive", "consolidate", "memoria",
    ],
    # ── Domínio: cardápio (o coração do site) ──
    "maltomaia-cardapio": [
        "cardapio", "categoria", "item", "preco", "disponivel", "destaque",
        "carro-chefe", "carros-chefe", "seed_cardapio", "cardapio/models.py",
        "cardapio/views.py", "cardapio/services.py", "configuracaosite",
        "a definir", "ordem", "menu", "indisponivel",
    ],
    # ── i18n PT/EN ──
    "maltomaia-i18n": [
        "i18n", "idioma", "bilingue", "bilíngue", "strings", "traducao",
        "tradução", "traduzir", "ingles", "inglês", "portugues", "português",
        "core/i18n.py", "set_language", "lang", "pt-br", "header", "rodape",
        "desc_pt", "desc_en", "nome_pt", "nome_en", "{% t",
    ],
    # ── Templates / design system ──
    "maltomaia-templates": [
        "templates/", "base.html", "malto.css", "site.css", "painel.css",
        "design", "brand", "eyebrow", "chip", "btn-primary", "paleta",
        "responsivo", "mobile", "playfair", "nunito", "var(--sun)", "static/css",
    ],
    # ── Mobile / responsivo (verificacao) ──
    "maltomaia-mobile": [
        "mobile", "celular", "responsivo", "responsive", "overflow",
        "scroll horizontal", "estourou", "estourando", "cortado", "cortou",
        "burger", "breakpoint", "viewport", "media query", "object-fit",
        "toque", "touch", "375px", "375", "preview_resize",
    ],
    # ── Deploy / infra Render ──
    "maltomaia-deploy": [
        "build.sh", "render.yaml", "procfile", "collectstatic", "gunicorn",
        "requirements.txt", "whitenoise", "deploy", "release", "neon",
        "postgres", "database_url", "runtime.txt", "createsuperuser",
    ],
    # ── Segurança / acesso ao painel ──
    "maltomaia-security": [
        "settings/prod.py", "settings/base.py", "axes", "login_required",
        "staff_required", "staff_member_required", "require_post", "password",
        "senha", "csrf", "hsts", "secure_", "secret", "lockout", "painel",
        "superuser", "seguranca", "segurança",
    ],
    # ── Validação antes de commit/deploy ──
    "maltomaia-validation": [
        "manage.py test", "manage.py check", "tests.py", "tests/",
        "test_", ".github/workflows", "makemigrations", "runserver",
        "validar", "testes", "smoke", "antes de commit", "antes de deploy",
        "antes de subir",
    ],
}


def build_index(verbose: bool = False) -> dict:
    index = {"generated": datetime.now(timezone.utc).isoformat(), "skills": {}}
    if not _SKILLS_DIR.exists():
        if verbose:
            print(f"  AVISO: {_SKILLS_DIR} não existe ainda")
        _INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False),
                               encoding="utf-8")
        return index
    for skill_dir in sorted(_SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print(f"  skip {skill_dir.name}: {e}")
            continue
        fm, body = _extract_frontmatter(text)
        name = fm.get("name") or skill_dir.name
        desc = fm.get("description", "")

        when_match = re.search(
            r"## Quando (?:disparar|rodar|invocar|usar)\s*\n(.+?)(?=\n## |\Z)",
            body, re.DOTALL | re.IGNORECASE,
        )
        when = when_match.group(1) if when_match else ""

        tokens = _tokenize(name) | _tokenize(desc) | _tokenize(when)
        for part in name.replace("-", "_").split("_"):
            if len(part) >= 3:
                tokens.add(part.lower())

        index["skills"][name] = {
            "path": str(skill_md.relative_to(_ROOT)).replace("\\", "/"),
            "description": desc[:300],
            "tokens": sorted(tokens),
            "path_hints": _PATH_HINTS.get(name, []),
            "when_excerpt": when.strip()[:500] if when else "",
        }
        if verbose:
            print(f"  indexed {name}: {len(tokens)} tokens")
    _INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    return index


def load_index(force_rebuild: bool = False) -> dict:
    if force_rebuild or not _INDEX_PATH.exists():
        return build_index(verbose=False)
    try:
        index = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return build_index(verbose=False)
    try:
        idx_mtime = _INDEX_PATH.stat().st_mtime
        for skill_dir in _SKILLS_DIR.iterdir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists() and skill_md.stat().st_mtime > idx_mtime:
                return build_index(verbose=False)
    except Exception:
        pass
    return index


# ──────────────────────────────────────────────────────────────────────
# Feedback storage
# ──────────────────────────────────────────────────────────────────────

def load_feedback() -> list[dict]:
    if not _FEEDBACK_PATH.exists():
        return []
    out = []
    try:
        for line in _FEEDBACK_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        pass
    return out


def append_feedback(task_id: str, query: str, skill: str, verdict: str,
                    note: str = "") -> None:
    record = {
        "task_id": task_id,
        "query": query[:500],
        "skill": skill,
        "verdict": verdict,
        "note": note[:200],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    with _FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────────────
# Classifier
# ──────────────────────────────────────────────────────────────────────

def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = a & b
    union = a | b
    return len(inter) / len(union) if union else 0.0


def _feedback_score(skill: str, query_tokens: set, fb_records: list[dict]) -> float:
    if not fb_records:
        return 0.0
    score = 0.0
    now = datetime.now(timezone.utc)
    for r in fb_records:
        if r.get("skill") != skill:
            continue
        q_toks = _tokenize(r.get("query", ""))
        sim = _jaccard(q_toks, query_tokens)
        if sim < 0.3:
            continue
        verdict = r.get("verdict", "neutral")
        weight = sim
        try:
            ts = datetime.fromisoformat(r.get("ts", ""))
            days = (now - ts).total_seconds() / 86400
            if days > 30:
                weight *= 0.5
        except Exception:
            pass
        if verdict == "ok":
            score += weight
        elif verdict == "nok":
            score -= weight
    return score


def classify(query: str, paths: list[str] | None = None,
             top_k: int = 3, index: dict | None = None,
             fb_records: list[dict] | None = None) -> list[dict]:
    if index is None:
        index = load_index()
    if fb_records is None:
        fb_records = load_feedback()
    paths = paths or []
    paths_str = " ".join(paths)
    full_text = f"{query} {paths_str}"
    q_tokens = _tokenize(full_text)

    results = []
    for skill_name, sdata in index["skills"].items():
        skill_tokens = set(sdata["tokens"])
        base = _jaccard(q_tokens, skill_tokens)

        path_bonus = 0.0
        for hint in sdata.get("path_hints", []):
            if hint.lower() in full_text.lower():
                path_bonus += 0.15
        path_bonus = min(path_bonus, 0.6)

        kw_bonus = 0.0
        for variant in (skill_name, skill_name.replace("-", "_"),
                        skill_name.replace("-", " ")):
            if variant.lower() in full_text.lower():
                kw_bonus += 0.3
        kw_bonus = min(kw_bonus, 0.5)

        fb_score = _feedback_score(skill_name, q_tokens, fb_records)
        fb_normalized = max(-0.3, min(0.3, fb_score * 0.1))

        total = base + path_bonus + kw_bonus + fb_normalized
        results.append({
            "skill": skill_name,
            "score": round(total, 3),
            "base": round(base, 3),
            "path_bonus": round(path_bonus, 3),
            "keyword_bonus": round(kw_bonus, 3),
            "feedback": round(fb_normalized, 3),
            "description": sdata.get("description", "")[:150],
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    results = [r for r in results if r["score"] >= 0.05]
    return results[:top_k]


# ──────────────────────────────────────────────────────────────────────
# Listener — service mode (inbox/outbox)
# ──────────────────────────────────────────────────────────────────────

def listen(poll_interval: float = 1.0, verbose: bool = True) -> None:
    if verbose:
        print("=== skill_router LISTEN START ===")
        print(f"  inbox:    {_INBOX_DIR}")
        print(f"  outbox:   {_OUTBOX_DIR}")
        print(f"  feedback: {_FEEDBACK_PATH}")
        print(f"  stop:     touch {_STOP_PATH}")
        print()
    while True:
        if _STOP_PATH.exists():
            try:
                _STOP_PATH.unlink()
            except Exception:
                pass
            if verbose:
                print("=== STOP detected — exiting ===")
            return
        index = load_index()
        fb = load_feedback()

        pending = sorted(_INBOX_DIR.glob("*.json"))
        for inbox_file in pending:
            try:
                data = json.loads(inbox_file.read_text(encoding="utf-8"))
                task_id = data.get("task_id") or inbox_file.stem
                query = data.get("query", "")
                paths = data.get("paths", [])
                top_k = data.get("top_k", 3)
                if verbose:
                    print(f"[INBOX] {task_id} query={query[:80]!r}")
                results = classify(query=query, paths=paths, top_k=top_k,
                                   index=index, fb_records=fb)
                out_data = {
                    "task_id": task_id,
                    "query": query,
                    "paths": paths,
                    "results": results,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
                outbox_file = _OUTBOX_DIR / inbox_file.name
                outbox_file.write_text(
                    json.dumps(out_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                if verbose:
                    if results:
                        top = results[0]
                        print(f"[OUTBOX] {task_id} -> {top['skill']} (score={top['score']})")
                    else:
                        print(f"[OUTBOX] {task_id} -> (no match)")
                processed_dir = _INBOX_DIR / "processed"
                processed_dir.mkdir(exist_ok=True)
                inbox_file.rename(processed_dir / inbox_file.name)
            except Exception as e:
                print(f"[ERR] {inbox_file.name}: {e}", file=sys.stderr)
                try:
                    err_dir = _INBOX_DIR / "errors"
                    err_dir.mkdir(exist_ok=True)
                    inbox_file.rename(err_dir / inbox_file.name)
                except Exception:
                    pass
        time.sleep(poll_interval)


# ──────────────────────────────────────────────────────────────────────
# CLI subcommands
# ──────────────────────────────────────────────────────────────────────

def cmd_classify(args) -> int:
    query = args.query or ""
    paths = args.paths or []
    if not query and not paths:
        print("ERR: passe query ou --paths", file=sys.stderr)
        return 2
    results = classify(query=query, paths=paths, top_k=args.top_k)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0
    if not results:
        print("(nenhuma skill matched — score < 0.05)")
        print("Regra do 'sem skill': PARE, reporte ao operador, não improvise.")
        return 0
    print(f"Top {len(results)} skills:")
    for i, r in enumerate(results, 1):
        print(f"\n  {i}. {r['skill']}  (score={r['score']})")
        print(f"     base={r['base']}  path+{r['path_bonus']}  "
              f"kw+{r['keyword_bonus']}  fb={r['feedback']:+.2f}")
        print(f"     {r['description']}")
    return 0


def cmd_listen(args) -> int:
    listen(poll_interval=args.poll, verbose=not args.quiet)
    return 0


def cmd_feedback(args) -> int:
    verdict = args.verdict.lower()
    if verdict not in {"ok", "nok", "neutral"}:
        print(f"ERR: verdict deve ser ok/nok/neutral, got {verdict!r}", file=sys.stderr)
        return 2
    query = args.query or ""
    if not query:
        p = _OUTBOX_DIR / f"{args.task_id}.json"
        if p.exists():
            try:
                query = json.loads(p.read_text(encoding="utf-8")).get("query", "")
            except Exception:
                pass
    append_feedback(args.task_id, query, args.skill, verdict, args.note or "")
    print(f"OK feedback gravado: {args.task_id} {args.skill} -> {verdict}")
    return 0


def cmd_stats(args) -> int:
    fb = load_feedback()
    if not fb:
        print("(sem feedback ainda)")
        return 0
    counts: dict[str, dict[str, int]] = {}
    for r in fb:
        skill = r.get("skill", "?")
        verdict = r.get("verdict", "neutral")
        counts.setdefault(skill, {"ok": 0, "nok": 0, "neutral": 0})
        counts[skill][verdict] = counts[skill].get(verdict, 0) + 1
    print(f"Total feedback: {len(fb)} records")
    print(f"\n{'skill':40s}  {'ok':>4}  {'nok':>4}  {'neu':>4}  net")
    print("-" * 70)
    rows = []
    for skill, c in counts.items():
        net = c.get("ok", 0) - c.get("nok", 0)
        rows.append((net, skill, c))
    rows.sort(key=lambda x: x[0], reverse=True)
    for net, skill, c in rows:
        print(f"{skill:40s}  {c.get('ok',0):>4}  {c.get('nok',0):>4}  {c.get('neutral',0):>4}  {net:+d}")
    return 0


def cmd_reindex(args) -> int:
    idx = build_index(verbose=True)
    print(f"\nindexed {len(idx['skills'])} skills -> {_INDEX_PATH}")
    return 0


def cmd_dump_index(args) -> int:
    idx = load_index()
    skill = args.skill
    if skill:
        data = idx["skills"].get(skill)
        if not data:
            print(f"ERR: skill {skill!r} não indexada", file=sys.stderr)
            print(f"Disponíveis: {list(idx['skills'].keys())}", file=sys.stderr)
            return 1
        print(json.dumps({skill: data}, indent=2, ensure_ascii=False))
    else:
        print(f"Indexed skills ({len(idx['skills'])}):")
        for name, data in idx["skills"].items():
            print(f"  {name}  ({len(data['tokens'])} tokens, "
                  f"{len(data.get('path_hints', []))} path hints)")
    return 0


def cmd_enqueue(args) -> int:
    task_id = args.task_id or uuid.uuid4().hex[:12]
    inbox_path = _INBOX_DIR / f"{task_id}.json"
    payload = {
        "task_id": task_id,
        "query": args.query or "",
        "paths": args.paths or [],
        "top_k": args.top_k,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    inbox_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(task_id)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="skill_router",
                                description="Roteia tarefas pra skill correta (Malto Maia)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_cls = sub.add_parser("classify", help="Classify ad-hoc (CLI)")
    p_cls.add_argument("query", nargs="?", default="", help="Texto da tarefa")
    p_cls.add_argument("--paths", nargs="+", default=[], help="Arquivos afetados")
    p_cls.add_argument("--top-k", type=int, default=3)
    p_cls.add_argument("--json", action="store_true")
    p_cls.set_defaults(func=cmd_classify)

    p_ls = sub.add_parser("listen", help="Service mode (inbox/outbox)")
    p_ls.add_argument("--poll", type=float, default=1.0)
    p_ls.add_argument("--quiet", action="store_true")
    p_ls.set_defaults(func=cmd_listen)

    p_fb = sub.add_parser("feedback", help="Grava feedback pra task")
    p_fb.add_argument("task_id")
    p_fb.add_argument("skill")
    p_fb.add_argument("verdict", help="ok / nok / neutral")
    p_fb.add_argument("--note", default="")
    p_fb.add_argument("--query", default="", help="Override query (se outbox sumiu)")
    p_fb.set_defaults(func=cmd_feedback)

    p_st = sub.add_parser("stats", help="Resumo do feedback acumulado")
    p_st.set_defaults(func=cmd_stats)

    p_ri = sub.add_parser("reindex", help="Força rebuild do index")
    p_ri.set_defaults(func=cmd_reindex)

    p_di = sub.add_parser("dump-index", help="Mostra index de uma skill")
    p_di.add_argument("skill", nargs="?", default="")
    p_di.set_defaults(func=cmd_dump_index)

    p_eq = sub.add_parser("enqueue", help="Enfileira task pro listener processar")
    p_eq.add_argument("--task-id", default="")
    p_eq.add_argument("--query", default="")
    p_eq.add_argument("--paths", nargs="+", default=[])
    p_eq.add_argument("--top-k", type=int, default=3)
    p_eq.set_defaults(func=cmd_enqueue)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
