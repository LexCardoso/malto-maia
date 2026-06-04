"""Marca o Café Espresso como carro-chefe (4o card de destaque da landing)."""
from django.db import migrations


def mark(apps, schema_editor):
    Item = apps.get_model("cardapio", "Item")
    Item.objects.filter(nome="Café Espresso").update(destaque=True)


def unmark(apps, schema_editor):
    Item = apps.get_model("cardapio", "Item")
    Item.objects.filter(nome="Café Espresso").update(destaque=False)


class Migration(migrations.Migration):
    dependencies = [("cardapio", "0004_seed_avaliacoes")]
    operations = [migrations.RunPython(mark, unmark)]
