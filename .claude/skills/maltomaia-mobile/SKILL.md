---
name: maltomaia-mobile
description: |
  Verificação mobile-first do site. Toda mudança em template/CSS PRECISA ser checada
  no celular (375px): zero scroll horizontal, header enxuto, toque grande, imagem com
  object-fit. Use SEMPRE depois de mexer em templates/ ou static/css, ou quando
  aparecer bug de layout no mobile. Traz o método de auditoria de overflow via preview.
---

# maltomaia-mobile

A maioria acessa pelo celular. Mobile-first não é opcional — é a régua. Esta skill diz
**o que checar** e **como medir** (não confiar no olho).

## Quando disparar

- **Depois de QUALQUER mudança em `templates/` ou `static/css/`** — antes de commitar.
- Bug de layout reportado no celular ("cortou", "estourou", "dá pra arrastar pro lado").
- Tela/seção nova.

## Breakpoints (em `site.css` / `responsive.css`)

- **920px** — a nav vira **burger**; a CTA "Fazer encomenda" e o toggle PT/EN somem do
  topo e vão pro menu do burger (`.mnav-foot`). Header no mobile = **só logo + burger**.
- **620px** — ajustes de telefone (grids viram 1 coluna, tabela do painel vira cards).
- **420px** — telas bem pequenas.

## A regra de ouro: ZERO scroll horizontal

Nada pode estourar a largura da viewport. O sintoma clássico (já aconteceu): header
lotado empurrando elementos pra fora → 95px de overflow em todas as páginas.

## Como medir (preview, não no olho)

`preview_inspect`/`preview_eval` são mais confiáveis que screenshot (que às vezes trava).
Suba o preview, `preview_resize` pro preset **mobile** (375px), e rode esta auditoria
em cada página (`/`, `/cardapio/`, `/encomenda/`, `/painel/entrar/`):

```js
(() => {
  const vw = document.documentElement.clientWidth;
  const wide = [];
  document.querySelectorAll('*').forEach(e => {
    const r = e.getBoundingClientRect();
    // ignora quem rola dentro de container overflow-x:auto/scroll (ex.: quicknav)
    let p = e.parentElement, inScroll = false;
    while (p) { const s = getComputedStyle(p); if (s.overflowX === 'auto' || s.overflowX === 'scroll') { inScroll = true; break; } p = p.parentElement; }
    if (!inScroll && r.right > vw + 1) wide.push({ cls: e.className, right: Math.round(r.right) });
  });
  return { bodyOverflowX: document.body.scrollWidth - vw, realWide: wide.sort((a,b)=>b.right-a.right).slice(0,6) };
})()
```

**`bodyOverflowX` tem que ser 0** e **`realWide` vazio**. Se houver algo, o `realWide`
aponta o elemento culpado (classe + onde a borda direita passa de 375).

> **Gotcha de dev:** o browser cacheia o `site.css` no runserver. Se o CSS novo não
> refletir, faça cache-bust (`link.href = '/static/css/site.css?cb=' + Date.now()`) ou
> reinicie o preview. **Em produção não acontece** (WhiteNoise versiona por hash).

## Checklist mobile

- [ ] `bodyOverflowX == 0` em todas as páginas a 375px.
- [ ] Header = logo + burger; CTA e idioma dentro do menu.
- [ ] Imagem em slot usa `object-fit: cover` (não distorce) — ver `.ph.has-photo > img`.
- [ ] Alvos de toque grandes (botão ≥ ~44px), bom contraste (público maduro).
- [ ] Grids viram 1 coluna; nada de fonte minúscula.

## Anti-patterns

- ❌ Commitar mudança de template/CSS sem abrir a 375px.
- ❌ "Resolver" overflow com `overflow-x: hidden` no body (esconde o sintoma, quebra
  sticky; some com conteúdo). Achar e consertar o elemento que estoura.
- ❌ Largura fixa em px que não cabe em 360-390px.
- ❌ **`aspect-ratio` + `min-height` num slot de foto**: o `min-height` impõe uma largura
  mínima (`min-height × ratio`) que estoura a tela no mobile. Use só `aspect-ratio` (a
  altura sai da largura). Foi o bug do hero/visit a 375px (herdado do design original).
- ❌ `margin: 0 auto` num grid item **sem `width`**: ele encolhe pro conteúdo em vez de
  esticar. Dê `width: 100%` se quer que preencha a coluna.
- ❌ Imagem sem `object-fit` (estica/distorce).

## Referências

- `static/css/site.css` (header, `.mnav-foot`, `.ph.has-photo`), `responsive.css`.
- Skills irmãs: `maltomaia-templates` (design system), `maltomaia-validation`.
