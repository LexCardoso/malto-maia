"""Reset unico dos bloqueios do django-axes (limpa AccessAttempt).

Operacional, roda uma vez por banco: destrava quem ficou preso pelo cooloff antigo
(1h). O axes segue ATIVO — daqui pra frente vale o novo cooloff curto (settings).
Em banco novo/limpo a tabela esta vazia, entao e um no-op inofensivo.
"""
from django.db import migrations


def reset_lockouts(apps, schema_editor):
    AccessAttempt = apps.get_model("axes", "AccessAttempt")
    AccessAttempt.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cardapio", "0007_recarrega_cardapio_real"),
        ("axes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(reset_lockouts, migrations.RunPython.noop),
    ]
