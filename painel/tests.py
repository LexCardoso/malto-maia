from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cardapio.models import Categoria, Item


class AcessoPainelTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(slug="q", nome_pt="Quentes", ordem=0)
        self.item = Item.objects.create(categoria=self.cat, nome="Espresso", preco="6.80")
        U = get_user_model()
        self.staff = U.objects.create_user("dono", password="senha-forte-123", is_staff=True)
        self.ze = U.objects.create_user("ze", password="senha-forte-123")

    def test_anonimo_redireciona_login(self):
        r = self.client.get(reverse("painel:dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/painel/entrar/", r.headers["Location"])

    def test_nao_staff_redireciona(self):
        self.client.force_login(self.ze)
        r = self.client.get(reverse("painel:dashboard"))
        self.assertEqual(r.status_code, 302)

    def test_staff_acessa_dashboard(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse("painel:dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Espresso")

    def test_toggle_disponibilidade(self):
        self.client.force_login(self.staff)
        self.assertTrue(self.item.disponivel)
        r = self.client.post(reverse("painel:item_toggle", args=[self.item.pk]))
        self.assertEqual(r.status_code, 302)
        self.item.refresh_from_db()
        self.assertFalse(self.item.disponivel)

    def test_toggle_exige_post(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse("painel:item_toggle", args=[self.item.pk]))
        self.assertEqual(r.status_code, 405)

    def test_editar_item_marca_data(self):
        self.client.force_login(self.staff)
        r = self.client.post(
            reverse("painel:item_editar", args=[self.item.pk]),
            {"categoria": self.cat.pk, "nome": "Espresso Duplo",
             "desc_pt": "", "desc_en": "", "preco": "7.50",
             "destaque": "", "disponivel": "on", "ordem": "0"},
        )
        self.assertEqual(r.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.nome, "Espresso Duplo")
