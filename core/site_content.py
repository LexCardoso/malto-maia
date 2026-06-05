"""Conteudo editavel do site: quais TEXTOS (chaves do i18n) e quais FOTOS (slots)
o dono pode trocar pelo painel. Override vazio = usa o i18n / o estatico padrao.

Mantido curado de proposito: so o conteudo que muda de vez em quando — nao todo
rotulo de botao. As FOTOS cobrem todos os slots visiveis do site.
"""

# (chave do i18n, secao, rotulo no painel, multilinha?)
TEXTOS_EDITAVEIS = [
    ("hero.eyebrow", "Hero", "Tarja (local)", False),
    ("hero.title", "Hero", "Título", True),
    ("hero.sub", "Hero", "Subtítulo", True),
    ("hero.badge", "Hero", "Selo (avaliação)", False),
    ("about.eyebrow", "Sobre", "Tarja", False),
    ("about.title", "Sobre", "Título", False),
    ("about.p1", "Sobre", "Parágrafo 1", True),
    ("about.p2", "Sobre", "Parágrafo 2", True),
    ("high.eyebrow", "Destaques", "Tarja", False),
    ("high.title", "Destaques", "Título", False),
    ("high.sub", "Destaques", "Subtítulo", True),
    ("gal.eyebrow", "Galeria", "Tarja", False),
    ("gal.title", "Galeria", "Título", False),
    ("order.eyebrow", "Encomenda", "Tarja", False),
    ("order.title", "Encomenda", "Título", False),
    ("order.sub", "Encomenda", "Texto", True),
    ("rev.eyebrow", "Avaliações", "Tarja", False),
    ("rev.title", "Avaliações", "Título", False),
    ("ig.eyebrow", "Instagram", "Tarja", False),
    ("ig.title", "Instagram", "Título", False),
    ("visit.eyebrow", "Visite", "Tarja", False),
    ("visit.title", "Visite", "Título", False),
    ("visit.addr", "Visite", "Endereço", True),
    ("visit.hours", "Visite", "Horário", False),
    ("concept.eyebrow", "Conceito", "Tarja", False),
    ("concept.title", "Conceito", "Título", False),
    ("concept.body", "Conceito", "Texto", True),
    ("menu.title", "Cardápio", "Título", False),
    ("menu.sub", "Cardápio", "Subtítulo", True),
]

# (slug, secao, rotulo, estatico padrao)
FOTOS_SITE = [
    ("hero", "Hero", "Foto grande do hero", "img/fotos/hero-cappuccino.jpg"),
    ("sobre-fachada", "Sobre", "Fachada (principal)", "img/fotos/fachada.jpg"),
    ("sobre-jardim", "Sobre", "Jardim (menor)", "img/fotos/gal-jardim.jpg"),
    ("galeria-1", "Galeria", "Galeria 1", "img/fotos/gal-mesa.jpg"),
    ("galeria-2", "Galeria", "Galeria 2", "img/fotos/gal-cafe.jpg"),
    ("galeria-3", "Galeria", "Galeria 3", "img/fotos/destaque-cappuccino.jpg"),
    ("galeria-4", "Galeria", "Galeria 4", "img/fotos/gal-lousa.jpg"),
    ("galeria-5", "Galeria", "Galeria 5 (larga)", "img/fotos/gal-interior.jpg"),
    ("galeria-6", "Galeria", "Galeria 6", "img/fotos/encomenda.jpg"),
    ("visite", "Visite", "Foto da entrada", "img/fotos/visite.jpg"),
    ("conceito", "Conceito", "Foto da lousa", "img/fotos/conceito.jpg"),
    ("ig-1", "Instagram", "Instagram 1", "img/fotos/hero-cappuccino.jpg"),
    ("ig-2", "Instagram", "Instagram 2", "img/fotos/destaque-torta.jpg"),
    ("ig-3", "Instagram", "Instagram 3", "img/fotos/destaque-pao-de-queijo.jpg"),
    ("ig-4", "Instagram", "Instagram 4", "img/fotos/gal-mesa.jpg"),
    ("ig-5", "Instagram", "Instagram 5", "img/fotos/gal-jardim.jpg"),
    ("ig-6", "Instagram", "Instagram 6", "img/fotos/gal-lousa.jpg"),
]

FOTO_DEFAULTS = {slug: default for slug, _sec, _lbl, default in FOTOS_SITE}
SLUGS_VALIDOS = set(FOTO_DEFAULTS)


def textos_overrides():
    """{chave: {pt, en}} dos textos sobrescritos no banco (cacheado)."""
    from django.core.cache import cache
    data = cache.get("textos_site")
    if data is None:
        from cardapio.models import TextoSite
        data = {ts.chave: {"pt": ts.pt, "en": ts.en} for ts in TextoSite.objects.all()}
        cache.set("textos_site", data, 60)
    return data


def fotos_overrides():
    """{slug: versao} das fotos que tem override no banco (cacheado)."""
    from django.core.cache import cache
    data = cache.get("fotos_site_map")
    if data is None:
        from cardapio.models import FotoSite
        data = {
            fs.slug: (int(fs.atualizado_em.timestamp()) if fs.atualizado_em else 0)
            for fs in FotoSite.objects.exclude(foto_mime="")
        }
        cache.set("fotos_site_map", data, 60)
    return data


def foto_site_url(slug):
    """URL da foto do slot: a do banco (se trocada) ou o estatico padrao."""
    from django.templatetags.static import static
    from django.urls import reverse
    ov = fotos_overrides()
    if slug in ov:
        return f"{reverse('cardapio:foto_site', args=[slug])}?v={ov[slug]}"
    default = FOTO_DEFAULTS.get(slug, "")
    return static(default) if default else ""
