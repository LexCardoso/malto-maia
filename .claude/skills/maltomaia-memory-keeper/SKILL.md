---
name: maltomaia-memory-keeper
description: |
  Gerencia o CICLO DE VIDA da memória persistente do projeto Malto Maia
  (memory/ — MEMORY.md + arquivos). Arquiva o que virou passado e mantém o índice
  MEMORY.md enxuto (< 24KB). Use quando MEMORY.md inchar, quando uma decisão/bug virar
  histórico, ou periodicamente pra podar acúmulo.
---

# maltomaia-memory-keeper

A memória persistente cresce sem parar (snapshots de sessão, bugs resolvidos, decisões
superseded). O índice `MEMORY.md` é carregado TODA sessão — se incha, o recall fica
caro/ruidoso. Este skill ARQUIVA o passado (sem perder, consultável) e mantém o índice
ativo enxuto.

Irmão do `anthropic-skills:consolidate-memory` (que MESCLA duplicados): aqui o foco é o
eixo TEMPO — mover passado → archive. Usar os dois juntos.

## Quando disparar

- `MEMORY.md` passou de ~24KB (o sistema avisa no boot).
- Sessão/bug RESOLVIDO virou histórico (não muda decisão futura).
- Decisão SUPERSEDED por outra mais nova.
- Periodicamente, pra podar acúmulo.
- Operador pede "arquiva o que é passado" / "limpa a memória".

## Classificação: ATIVO vs PASSADO

| ATIVO (fica em MEMORY.md) | PASSADO (vai pra archive/) |
|---|---|
| Regra/convenção em vigor (PT-BR, bilíngue, preço null="a definir", no-emoji) | Snapshot de sessão antiga já consolidado |
| Estado de produção atual (URL, plano Render, env crítico, banco) | Bug resolvido + verificado |
| Tarefa EM ANDAMENTO (ex.: "integrar layout final do design") | Decisão superseded |
| Referência recorrente (paleta, mapa de apps, fluxo de deploy) | Plano já executado |
| Gap conhecido ainda aberto | Gap já fechado |

**Regra de ouro**: se o item NÃO mudaria nenhuma decisão na próxima sessão, é PASSADO.
Em dúvida → ATIVO.

## Processo

1. Ler `MEMORY.md` inteiro + medir tamanho.
2. Classificar cada linha (ATIVO/PASSADO).
3. Para cada PASSADO: mover a linha do índice → `archive/MEMORY_ARCHIVE.md` (com data),
   mover o arquivo `.md` → `memory/archive/` (preservar frontmatter, não reescrever).
4. Consolidar passado redundante (N snapshots da semana → 1 resumo no archive).
5. Verificar `MEMORY.md` < 24KB.
6. `MEMORY_ARCHIVE.md` sempre lista o que foi arquivado + como consultar.

## Regras

- **NUNCA deletar** — só mover pro archive (auditoria, "por que decidimos X").
- Arquivar ≠ mesclar (duplicado de 2 ATIVOS é trabalho do `consolidate-memory`).
- Manter ponteiros `[[link]]`.
- Preservar frontmatter e conteúdo ao mover.

## Anti-patterns

- ❌ Arquivar regra em vigor (bilíngue, PT-BR, no-emoji) — é ATIVO sempre.
- ❌ Arquivar tarefa em andamento porque a linha é longa — encurta a linha.
- ❌ Deletar em vez de arquivar.
- ❌ Archive virar lixeira sem índice.

## Referências

- `anthropic-skills:consolidate-memory` — mescla duplicados (complementar).
- Regras de memória do sistema (frontmatter, tipos, MEMORY.md como índice).
- `maltomaia-skill-router` — meta-skill irmã.
