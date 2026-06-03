from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from cardapio.models import Categoria, ConfiguracaoSite, Item
from cardapio.services import menu_localizado
from core.templatetags.maltomaia import brl


class SeedTests(TestCase):
    def test_seed_popula_e_e_idempotente(self):
        call_command("seed_cardapio")
        n_cat = Categoria.objects.count()
        n_item = Item.objects.count()
        self.assertGreater(n_cat, 0)
        self.assertGreater(n_item, 0)
        # Rodar de novo não duplica nem apaga (idempotente).
        call_command("seed_cardapio")
        self.assertEqual(Categoria.objects.count(), n_cat)
        self.assertEqual(Item.objects.count(), n_item)

    def test_seed_force_recria(self):
        call_command("seed_cardapio")
        Item.objects.first().delete()
        antes = Item.objects.count()
        call_command("seed_cardapio", "--force")
        self.assertGreater(Item.objects.count(), antes)


class MenuRenderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cardapio")

    def test_menu_renderiza_item(self):
        r = self.client.get(reverse("cardapio:menu"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Cappuccino Mineiro")

    def test_preco_nulo_mostra_a_definir(self):
        cat = Categoria.objects.create(slug="x", nome_pt="X", ordem=99)
        Item.objects.create(categoria=cat, nome="Item Sem Preco", preco=None)
        r = self.client.get(reverse("cardapio:menu"))
        self.assertContains(r, "a definir")


class BrlFilterTests(TestCase):
    def test_formata_brl(self):
        self.assertEqual(brl(Decimal("6.80")), "R$ 6,80")
        self.assertEqual(brl(Decimal("1234.5")), "R$ 1.234,50")

    def test_none_vazio(self):
        self.assertEqual(brl(None), "")


class LocalizacaoTests(TestCase):
    def test_services_localiza_en(self):
        cat = Categoria.objects.create(slug="c", nome_pt="Quentes", nome_en="Hot", ordem=0)
        Item.objects.create(categoria=cat, nome="Espresso", desc_pt="70 ml", desc_en="70 ml EN")
        dados = menu_localizado("en")
        self.assertEqual(dados[0]["nome"], "Hot")
        self.assertEqual(dados[0]["itens"][0]["desc"], "70 ml EN")

    def test_config_singleton(self):
        a = ConfiguracaoSite.get()
        b = ConfiguracaoSite.get()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(ConfiguracaoSite.objects.count(), 1)


class QrTests(TestCase):
    def test_qr_svg(self):
        r = self.client.get(reverse("cardapio:menu_qr"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "image/svg+xml")
        self.assertIn(b"<svg", r.content)
