"""Helpers de leitura do cardapio, ja localizados (PT/EN)."""
from django.db.models import Prefetch
from django.templatetags.static import static
from django.urls import reverse

from .models import Categoria, Item

# Placeholder (em static/) de cada carro-chefe, por nome do item. So entra em acao
# quando o produto AINDA nao tem foto propria no banco (item.tem_foto == False).
DESTAQUE_IMAGENS = {
    "Cappuccino Mineiro": "img/fotos/destaque-cappuccino.jpg",
    "Pão de Queijo": "img/fotos/destaque-pao-de-queijo.jpg",
    # torta de coco (assinatura da casa) — foto real
    "Torta — fatia": "img/fotos/destaque-torta.jpg",
    "Café Espresso": "img/fotos/gal-cafe.jpg",
}


def _foto_url(item):
    """URL publica da foto do produto (ou "" se nao tiver). Com cache-buster pela
    data de atualizacao, pra trocar a foto invalidar o cache do navegador."""
    if not item.tem_foto:
        return ""
    v = int(item.atualizado_em.timestamp()) if item.atualizado_em else 0
    return f"{reverse('cardapio:item_foto', args=[item.id])}?v={v}"


def _destaque_imagem(item):
    """Foto do destaque: a do proprio produto se existir; senao o placeholder fixo."""
    propria = _foto_url(item)
    if propria:
        return propria
    nome_static = DESTAQUE_IMAGENS.get(item.nome, "")
    return static(nome_static) if nome_static else ""


def menu_localizado(lang="pt", apenas_disponiveis=False, apenas_encomendaveis=False):
    """Lista de categorias -> dict com nome/nota/itens ja no idioma pedido.

    apenas_encomendaveis=True (pagina de encomenda): so itens com encomendavel=True.
    Os bytes da foto NAO sao carregados aqui (defer) — so o foto_url/tem_foto.
    """
    categorias = Categoria.objects.prefetch_related(
        Prefetch("itens", queryset=Item.objects.defer("foto"))
    ).all()
    resultado = []
    for c in categorias:
        itens = [
            i for i in c.itens.all()
            if (i.disponivel or not apenas_disponiveis)
            and (i.encomendavel or not apenas_encomendaveis)
        ]
        if not itens:
            continue
        resultado.append(
            {
                "slug": c.slug,
                "nome": c.nome(lang),
                "nota": c.nota(lang),
                "itens": [
                    {
                        "id": i.id,
                        "nome": i.nome,
                        "desc": i.desc(lang),
                        "preco": i.preco,
                        "destaque": i.destaque,
                        "disponivel": i.disponivel,
                        "tem_foto": i.tem_foto,
                        "foto_url": _foto_url(i),
                    }
                    for i in itens
                ],
            }
        )
    return resultado


def destaques_localizados(lang="pt", limite=4):
    """Carros-chefe disponiveis para a landing."""
    itens = (
        Item.objects.filter(destaque=True, disponivel=True)
        .select_related("categoria")
        .defer("foto")[:limite]
    )
    return [
        {
            "id": i.id,
            "nome": i.nome,
            "desc": i.desc(lang),
            "preco": i.preco,
            "categoria": i.categoria.nome(lang),
            "imagem_url": _destaque_imagem(i),
        }
        for i in itens
    ]
