---
name: maltomaia-cardapio
description: |
  O coração do site: o cardápio. Modelos Categoria/Item/ConfiguracaoSite, regra do
  preço "a definir" (null), carro-chefe (destaque), disponibilidade, o seed idempotente
  e o painel de edição. Use ao mexer em cardapio/ (models, services, views, seed),
  no painel/ de edição, ou quando o conteúdo do menu mudar.
---

# maltomaia-cardapio

O dono loga no painel e edita o cardápio que aparece no site. Essa é a feature
central — tudo gira em torno de manter esse fluxo simples e à prova de erro.

## Modelo de dados (`cardapio/models.py`)

- **Categoria**: `slug`, `nome_pt`/`nome_en`, `nota_pt`/`nota_en` (subtítulo), `ordem`.
- **Item**: FK `categoria`, `nome` (não traduz), `desc_pt`/`desc_en`, `preco`
  (Decimal **null = "a definir"**), `destaque` (carro-chefe), `disponivel`, `ordem`.
- **ConfiguracaoSite**: singleton (pk=1) — `cardapio_atualizado_em` (data exibida no
  menu), `whatsapp`, `instagram`. Pegue sempre via `ConfiguracaoSite.get()`.

## Regras invioláveis

1. **`preco = None` significa "a definir"** — nunca renderize `R$ 0,00`. O template
   checa `{% if i.preco %}` e cai pra `{% t 'common.askPrice' %}`. A encomenda
   exclui itens sem preço do total (vão com nota "a definir").
2. **Item indisponível continua no cardápio**, marcado como tal (`.off` + tag), mas
   **some da encomenda** (`menu_localizado(apenas_disponiveis=True)`).
3. **Toda edição no painel chama `ConfiguracaoSite.get().marcar_atualizado_hoje()`**
   pra a data "Atualizado em" do menu ficar correta.
4. **Leitura sempre via `cardapio/services.py`** (`menu_localizado`, `destaques_localizados`)
   — já vem localizado PT/EN e com `select_related`/`prefetch_related`. Não refazer
   query crua na view.
5. **Carro-chefe** (`destaque=True` + `disponivel=True`) alimenta a seção de
   destaques da landing (`destaques_localizados`).

## Seed (`management/commands/seed_cardapio.py`)

- Espelha `assets/menu-data.js` do design. **Idempotente**: só popula se o banco
  estiver vazio (`Categoria.objects.exists()`), pra **nunca sobrescrever** edições
  do dono. `--force` apaga e recria (use só em dev/reset consciente).
- `build.sh` roda `seed_cardapio` a cada deploy — por isso a idempotência é crítica.

## Quando disparar

- Mexer em `cardapio/` (models, services, views, admin, seed).
- Mexer no `painel/` de edição (forms, views de CRUD do item).
- Adicionar campo ao Item/Categoria (→ também `maltomaia-i18n` se for bilíngue,
  `maltomaia-validation` pra migration).
- Mudar a lógica de preço/disponibilidade/destaque.

## Anti-patterns

- ❌ Renderizar preço null como 0 ou vazio sem o rótulo "a definir".
- ❌ Query de Item/Categoria na view sem passar por `services.py`.
- ❌ Seed que sobrescreve dados existentes sem `--force` explícito.
- ❌ Editar item e esquecer de atualizar a data do cardápio.
- ❌ Adicionar texto bilíngue só em PT (ver `maltomaia-i18n`).

## Referências

- `cardapio/models.py`, `cardapio/services.py`, `cardapio/management/commands/seed_cardapio.py`
- `painel/views.py`, `painel/forms.py` — edição.
- Skills irmãs: `maltomaia-i18n`, `maltomaia-templates`, `maltomaia-validation`.
