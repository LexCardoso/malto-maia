---
name: maltomaia-validation
description: |
  Pirâmide de validação antes de commit/deploy: manage.py check → makemigrations --check
  → manage.py test → collectstatic (prod) → smoke no runserver. Espelha o CI
  (.github/workflows/test.yml). Use sempre que mudar código que afeta comportamento.
---

# maltomaia-validation

Validação proporcional ao risco. Cobertura de teste ainda é fina, então a disciplina
manual importa. Use o venv do projeto: `venv\Scripts\python.exe` (Windows).

## A pirâmide (rápido → completo)

```
1. manage.py check                         (segundos) — config/deploy sãos?
2. makemigrations --check --dry-run        (segundos) — model sem migration?
3. manage.py test                          (segundos) — testes não quebraram?
4. collectstatic --settings=...prod        (segundos) — manifest não acha estático quebrado?
5. runserver + smoke das telas afetadas    (1 min)    — sobem sem 500?
```

```bash
venv\Scripts\python.exe manage.py check
venv\Scripts\python.exe manage.py makemigrations --check --dry-run
venv\Scripts\python.exe manage.py test
venv\Scripts\python.exe manage.py collectstatic --noinput --settings=maltomaia.settings.prod
venv\Scripts\python.exe manage.py runserver   # abrir / , /cardapio/ , /encomenda/ , /painel/
```

## Qual checagem pra qual mudança

| Mudança | Mínimo a rodar |
|---|---|
| View / form / lógica | check + test + smoke da tela |
| Model | check + **makemigrations --check** + migrate dev + test |
| Template (HTML) | check + smoke visual (PT e EN) |
| CSS / estático | **collectstatic prod** (manifest valida refs) + smoke |
| settings / env | check (com o settings alvo) + smoke |
| i18n (string nova) | conferir PT **e** EN; `monitor --only i18n` |
| Cardápio (seed/model) | + rodar com banco vazio pra validar idempotência do seed |

## Protocolo antes de commit (mínimo inegociável)

1. `manage.py check` limpo.
2. `makemigrations --check` rc=0 (ou a migration está no commit).
3. `manage.py test` passa.
4. Mexeu em estático? `collectstatic` com prod roda sem erro de manifest.
5. Mudança visual/comportamental? Subiu a tela e confirmou (sem 500), nos dois idiomas.

O CI (`.github/workflows/test.yml`) roda `migrate` + `test` com `settings.dev`. Passou
local com dev, passa no CI.

## Smoke rápido (test client, sem subir servidor)

Há um caminho de smoke documentado: `Client()` com `settings.ALLOWED_HOSTS += ["testserver"]`,
GET em `/`, `/cardapio/`, `/encomenda/`, `/painel/` (302 → login), `/painel/entrar/`.

## Quando disparar

- Antes de qualquer commit que mude comportamento.
- Depois de gerar migration.
- Depois de mexer em CSS/estático.
- Antes de deploy.

## Anti-patterns

- ❌ Commitar sem `manage.py check`.
- ❌ Mexer em estático e não rodar `collectstatic` prod (manifest quebra o build do Render).
- ❌ "Passa no meu navegador" sem rodar os testes.
- ❌ Rodar com o python global (sem Django) — sempre o venv.

## Referências

- `.github/workflows/test.yml` — o CI que você espelha.
- `scripts/dev/monitor.py` — vigia determinístico complementar.
- Skills irmãs: `maltomaia-deploy`, `maltomaia-cardapio`.
