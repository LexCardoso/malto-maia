"""Helpers de leitura do cardapio, ja localizados (PT/EN)."""
from .models import Categoria


def menu_localizado(lang="pt", apenas_disponiveis=False):
    """Lista de categorias -> dict com nome/nota/itens ja no idioma pedido."""
    categorias = Categoria.objects.prefetch_related("itens").all()
    resultado = []
    for c in categorias:
        itens = [i for i in c.itens.all() if i.disponivel or not apenas_disponiveis]
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
        }
        for i in itens
    ]
