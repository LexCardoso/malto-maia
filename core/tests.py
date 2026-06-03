from django.test import TestCase, override_settings
from django.urls import reverse


class LandingTests(TestCase):
    def test_landing_200(self):
        r = self.client.get(reverse("core:landing"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Malto Maia")

    def test_landing_seo(self):
        r = self.client.get(reverse("core:landing"))
        self.assertContains(r, 'property="og:title"')
        self.assertContains(r, "CafeOrCoffeeShop")  # JSON-LD

    def test_health(self):
        r = self.client.get(reverse("core:health"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, b"ok")


class LanguageToggleTests(TestCase):
    def test_toggle_en_seta_sessao(self):
        self.client.get(reverse("core:set_language", args=["en"]))
        self.assertEqual(self.client.session.get("lang"), "en")

    def test_toggle_lang_invalido_ignora(self):
        self.client.get(reverse("core:set_language", args=["xx"]))
        self.assertIsNone(self.client.session.get("lang"))


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class ErrorPageTests(TestCase):
    def test_404_branded(self):
        r = self.client.get("/rota-que-nao-existe/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Página não encontrada", status_code=404)
