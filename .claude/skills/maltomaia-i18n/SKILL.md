---
name: maltomaia-i18n
description: |
  Disciplina bilíngue PT-BR / EN do site. Toda string de UI vive em core/i18n.py
  (STRINGS) e sai via {% t "chave" %}; todo conteúdo de cardápio tem campos *_pt/*_en.
  Use ao adicionar/editar qualquer texto visível, criar tela nova, ou mexer no toggle
  de idioma. Regra de ouro: nada novo entra só em um idioma.
---

# maltomaia-i18n

O site é mobile-first **e bilíngue** (PT-BR padrão, EN no toggle do header). Idioma
fica em `request.session['lang']`, definido pelo `core.middleware.LanguageMiddleware`
em `request.LANG`, trocado por `/idioma/<lang>/`.

## Dois canais de tradução

1. **Strings de interface** → `core/i18n.py` no dict `STRINGS` (`{"chave": {"pt": ..., "en": ...}}`).
   No template: `{% load maltomaia %}{% t "hero.title" %}`. No Python: `t(key, lang)`.
   Porte de `assets/i18n.js` do design — mantenha as chaves alinhadas.
2. **Conteúdo do cardápio** → campos `*_pt` / `*_en` dos modelos. `services.py` resolve
   pelo `lang` (`item.desc(lang)`, `categoria.nome(lang)`). O `nome` do item NÃO traduz.

## Regra de ouro

**Nada novo entra só em um idioma.** Toda chave em `STRINGS` precisa de `pt` E `en`.
Todo campo bilíngue de modelo precisa dos dois. Se o EN ainda não existe, repita o PT
como placeholder consciente — nunca deixe a chave sem o lado EN (o `monitor --only i18n`
flaga isso).

## Padrões

- Fallback do `t()`: `en` ausente → cai pra `pt` → cai pra própria chave. Seguro mas
  silencioso; não confie nele pra "esquecer" o EN.
- Título com quebra de linha (hero): a string tem `\n`; renderize com
  `{% t 'hero.title' as v %}{{ v|linebreaksbr }}`.
- O toggle PT|EN preserva a página via `?next={{ request.path|urlencode }}`.
- Preço é formatado pelo filtro `brl` (sempre `R$ 1.234,56`), independente de idioma.

## Quando disparar

- Adicionar/editar qualquer texto visível ao usuário.
- Criar tela/seção nova (precisa de chaves nos dois idiomas).
- Mexer no `LanguageMiddleware`, no `set_language`, ou no `context_processors.site_context`.
- Adicionar campo de conteúdo a um modelo (decidir se é bilíngue).

## Anti-patterns

- ❌ Hardcodar texto de UI no template em vez de `{% t %}`.
- ❌ Adicionar chave em `STRINGS` só com `pt`.
- ❌ Traduzir o `nome` do item (só `desc` é bilíngue).
- ❌ Ler conteúdo do cardápio sem passar pelo `services.py` (perde a localização).

## Referências

- `core/i18n.py` (STRINGS), `core/templatetags/maltomaia.py` (tag `t`, filtro `brl`).
- `core/middleware.py`, `core/context_processors.py`, `core/views.py` (`set_language`).
- Skill irmã: `maltomaia-cardapio` (campos *_pt/*_en), `maltomaia-templates`.
