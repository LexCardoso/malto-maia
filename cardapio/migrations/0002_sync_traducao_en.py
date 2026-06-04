"""Sincroniza as descricoes EN (corrigidas no seed) para itens ja existentes.

Em banco novo isto e no-op (migrate roda antes do seed, com banco vazio). No banco
de producao ja populado, aplica as correcoes de ingles do desc_en sem tocar em
nome/preco/disponibilidade/desc_pt (nao sobrescreve edicoes do dono nesses campos).
"""
from django.db import migrations


def sync_en(apps, schema_editor):
    try:
        from cardapio.management.commands.seed_cardapio import MENU
    except Exception:
        return
    Item = apps.get_model("cardapio", "Item")
    Categoria = apps.get_model("cardapio", "Categoria")
    for cat in MENU:
        try:
            categoria = Categoria.objects.get(slug=cat["slug"])
        except Categoria.DoesNotExist:
            continue
        for nome, _desc_pt, desc_en, _preco, _destaque in cat["itens"]:
            Item.objects.filter(categoria=categoria, nome=nome).update(desc_en=desc_en)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("cardapio", "0001_initial")]
    operations = [migrations.RunPython(sync_en, noop)]
