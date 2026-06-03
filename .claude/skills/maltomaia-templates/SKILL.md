---
name: maltomaia-templates
description: |
  Design system e templates do site (rústico-aconchegante, elegância artesanal).
  Paleta creme/espresso/sol, Playfair + Nunito Sans, classes de malto.css/site.css/
  painel.css, mobile-first. Use ao mexer em templates/, CSS, header/footer, ou ao
  construir tela nova que precisa ficar on-brand.
---

# maltomaia-templates

Visual **rústico-aconchegante com elegância artesanal** — caseiro e quente, mas
curado. NÃO é "praia/balada colorida". Mobile-first (a maioria acessa pelo celular).

## Paleta (tokens em `static/css/malto.css` `:root`)

- `--cream #F7F1E6` (base, respiro) · `--espresso #3B2A20` (texto) ·
  `--terracota #C0623B` (a telha) · **`--sun #F5A623` (assinatura / CTAs)** ·
  `--leaf #5E6B4F` (acento natural).
- Tipografia: `--display` Playfair Display (títulos), `--body` Nunito Sans (corpo),
  `--script` Caveat (só detalhes tipo lousa, com parcimônia — classe `.eyebrow`).

## Folhas de estilo

- `malto.css` — **design system** (tokens, `.btn*`, `.card`, `.chip`, `.section`,
  `.wrap`, `.eyebrow`, `.ph` placeholders de foto). Veio do design; não reescrever.
- `site.css` — **layout das páginas** (header, hero, seções, footer, cardápio, encomenda).
- `painel.css` — **admin** (tabela, stats, login, `.adm-input`).
- `responsive.css` — breakpoints e regras de impressão (Exportar PDF do cardápio).

## Estrutura de templates

- `templates/base.html` — shell público (header com logo+nav+toggle PT/EN+CTA, footer,
  bloco de `messages`/toast). Blocos: `title`, `extra_head`, `content`, `extra_scripts`.
- `templates/painel/base_painel.html` — shell do admin (sóbrio, coerente com a marca).
- Páginas estendem o shell certo e usam as classes existentes.

## Padrões

- Botões: `.btn-primary` (sol) = CTA principal; `.btn-wa` (verde) = WhatsApp;
  `.btn-ghost` = secundário; `.btn-terra`/`.btn-solid` = variações.
- Foto é protagonista, mas ainda não há upload: use `.ph` / `.ph-coffee` com
  `data-label="..."` como placeholder quente (gradiente) até entrarem fotos reais.
- Toque/alvo grande, bom contraste (público maduro). Reuse `.section`, `.wrap`, `.card`.
- Mudou CSS/estático? Rode `collectstatic` no deploy (WhiteNoise + ManifestStorage
  já fazem cache-busting por hash; ver `maltomaia-deploy`).

## Quando disparar

- Mexer em `templates/` ou em `static/css|js`.
- Construir tela/seção nova (manter on-brand e responsiva).
- Ajustar header, footer, toggle de idioma, navegação.
- Integrar o layout final que o operador entregar.

## Anti-patterns

- ❌ Cor fora da paleta / fonte fora de Playfair+Nunito (Caveat só em detalhe).
- ❌ Reescrever `malto.css` (é o design system; estenda em `site.css`).
- ❌ Quebrar mobile (testar < 620px; nav vira burger < 920px).
- ❌ Hardcodar texto sem `{% t %}` (ver `maltomaia-i18n`).

## Referências

- `static/css/{malto,site,painel,responsive}.css`, `templates/`.
- Design original: o zip do Claude Design (screens + assets).
- Skills irmãs: `maltomaia-i18n`, `maltomaia-cardapio`.
