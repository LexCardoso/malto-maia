"""Helpers de leitura do cardapio, ja localizados (PT/EN)."""
from .models import Categoria

# Foto (em static/) de cada carro-chefe da landing, por nome do item. Item sem
# entrada aqui cai no placeholder .ph (ex.: torta de coco — foto ainda pendente).
DESTAQUE_IMAGENS = {
    "Cappuccino Mineiro": "img/fotos/destaque-cappuccino.jpg",
    "Pão de Queijo": "img/fotos/destaque-pao-de-queijo.jpg",
    # placeholder temporario (bolo de cenoura) ate ter foto da torta de coco
    "Torta — fatia": "img/fotos/destaque-torta.jpg",
    "Café Espresso": "img/fotos/gal-cafe.jpg",
}


def menu_localizado(lang="pt", apenas_disponiveis=False, apenas_encomendaveis=False):
    """Lista de categorias -> dict com nome/nota/itens ja no idioma pedido.

    apenas_encomendaveis=True (pagina de encomenda): so itens com encomendavel=True.
    """
    categorias = Categoria.objects.prefetch_related("itens").all()
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
                    }
                    for i in itens
                ],
            }
        )
    return resultado


def destaques_localizados(lang="pt", limite=4):
    """Carros-chefe disponiveis para a landing."""
    from .models import Item

    itens = (
        Item.objects.filter(destaque=True, disponivel=True)
        .select_related("categoria")[:limite]
    )
    return [
        {
            "nome": i.nome,
            "desc": i.desc(lang),
            "preco": i.preco,
            "categoria": i.categoria.nome(lang),
            "imagem": DESTAQUE_IMAGENS.get(i.nome, ""),
        }
        for i in itens
    ]
