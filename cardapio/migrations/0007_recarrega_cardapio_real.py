"""Limpa o cardapio antigo (placeholder) para o seed recarregar o cardapio REAL.

O build.sh roda `migrate` e logo depois `seed_cardapio` (idempotente). Esta migration
apaga Categoria/Item; com a tabela vazia, o seed seguinte repopula com os dados reais
das fotos (ver management/commands/seed_cardapio.py). Roda uma unica vez por banco.

Nao mexe em Avaliacao nem no singleton ConfiguracaoSite (o seed atualiza o contato).
"""
from django.db import migrations


def limpa_cardapio(apps, schema_editor):
    Item = apps.get_model("cardapio", "Item")
    Categoria = apps.get_model("cardapio", "Categoria")
    Item.objects.all().delete()
    Categoria.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cardapio", "0006_avaliacao_ref"),
    ]

    operations = [
        migrations.RunPython(limpa_cardapio, migrations.RunPython.noop),
    ]
