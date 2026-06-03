---
name: maltomaia-skill-router
description: |
  Meta-skill: roteia a tarefa atual pra skill correta via scripts/dev/skill_router.py.
  Use SEMPRE no início de uma sessão ou ao começar tarefa nova (editar cardápio, model,
  template, i18n, config, deploy, bug) — ANTES de propor solução. Classifica via
  keywords + paths + feedback acumulado; o operador ensina via feedback CLI.
---

# maltomaia-skill-router

Meta-skill — roteador centralizado que aprende. Tira da cabeça a decisão de
"qual skill" e coloca num índice queryable + histórico de feedback que evolui.
Porte da arquitetura do imob_teams (que portou do trader_agent) pra Malto Maia.

> Rodar de dentro da raiz do projeto (onde está o `manage.py`). O script resolve
> os paths sozinho via `__file__`, então funciona de qualquer cwd.

## Como funciona

```
Claude começa tarefa nova
        │
        ▼
python scripts/dev/skill_router.py classify "descrição" --paths arquivo.py
        │
        ▼
Output: top-K skills com score
   1. maltomaia-cardapio   0.45
   2. maltomaia-i18n       0.20
        │
        ▼
Claude lê SKILL.md das top-K → aplica as regras
        │
        ▼
Operador marca feedback (ok / nok) → router aprende
```

## Comandos essenciais

```bash
# Classificar
python scripts/dev/skill_router.py classify "vou mexer no preço de um item"
python scripts/dev/skill_router.py classify --paths cardapio/models.py "campo novo"
python scripts/dev/skill_router.py classify "<query>" --json

# Feedback (operador ensina)
python scripts/dev/skill_router.py feedback <task_id> maltomaia-cardapio ok
python scripts/dev/skill_router.py feedback <task_id> maltomaia-i18n nok --note "era deploy"
python scripts/dev/skill_router.py stats

# Manutenção (após criar/editar uma SKILL.md)
python scripts/dev/skill_router.py reindex
python scripts/dev/skill_router.py dump-index maltomaia-cardapio
```

## Quando invocar o router

**SEMPRE** ao começar trabalho novo. Especialmente:

- Operador descreve nova tarefa ("vou mexer em X", "tem um bug em Y").
- Eu identifico que vou tocar em model/template/view/i18n/config/deploy.
- Trocar de contexto na sessão (terminei um fix, vou começar uma feature).
- Em dúvida sobre qual skill aplica.

**Quando NÃO invocar**: continuação imediata da mesma tarefa, tarefa trivial sem
skill mapeada (ler arquivo, `ls`), resposta puramente conversacional.

## Regra do "sem skill" — não improvisar

Se o router retorna **vazio** ou **todos os scores < 0.10**, NÃO propor solução:

1. **Parar** e reportar ao operador (é tarefa nova/única? lacuna real que vale uma
   skill nova? combinação que outra skill já cobre e eu errei a busca?).
2. **Esperar resposta** antes de qualquer edit.
3. Se "vale criar skill": `mkdir .claude/skills/maltomaia-<nome>/`, criar `SKILL.md`
   com frontmatter `name` + `description`, adicionar `_PATH_HINTS` no
   `scripts/dev/skill_router.py` se aplicável, `reindex`, validar com `classify`.
4. Se "tarefa única": prossigo com nota. Se "outra cobre": `feedback ok` na apontada.

## Skills atuais

`maltomaia-skill-router` (meta), `maltomaia-cardapio` (domínio), `maltomaia-i18n`,
`maltomaia-templates`, `maltomaia-deploy`, `maltomaia-security`,
`maltomaia-validation`, `maltomaia-memory-keeper`. Agente: `monitor`
(`.claude/agents/monitor.md`).

## Anti-patterns

- ❌ Propor solução sem invocar router primeiro.
- ❌ Ignorar top-1 do router sem motivo (se score > 0.30).
- ❌ Não dar feedback quando operador valida (`ok`) ou corrige (`nok`).
- ❌ Editar `state.json` na mão — sempre `reindex`.

## Referências

- `scripts/dev/skill_router.py` — implementação (stdlib only).
- `data/skill_router/` — inbox/outbox/feedback/state (runtime, gitignored salvo feedback).
- `.claude/agents/monitor.md` — guardião read-only.
