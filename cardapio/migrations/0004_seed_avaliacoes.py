"""Popula as 3 avaliacoes iniciais (so se nao houver nenhuma — idempotente)."""
from django.db import migrations

DADOS = [
    ("Marina R.", "O melhor espresso da região, num ambiente que dá vontade de não ir "
     "embora. A torta de coco é obrigatória.", 5, "google"),
    ("Paulo C.", "Casinha charmosa, atendimento caprichado e cappuccino mineiro "
     "maravilhoso. Voltarei sempre.", 5, "tripadvisor"),
    ("Helena M.", "Lugar de bom gosto, perfeito para um café tranquilo. O pão de queijo "
     "derrete na boca.", 5, "google"),
]


def seed(apps, schema_editor):
    Avaliacao = apps.get_model("cardapio", "Avaliacao")
    if Avaliacao.objects.exists():
        return
    for i, (autor, texto, nota, fonte) in enumerate(DADOS):
        Avaliacao.objects.create(
            autor=autor, texto=texto, nota=nota, fonte=fonte, aparece=True, ordem=i
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("cardapio", "0003_avaliacao_configuracaosite_latitude_and_more")]
    operations = [migrations.RunPython(seed, noop)]
