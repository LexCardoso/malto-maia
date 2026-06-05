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

    def test_toggle_ajax_retorna_json(self):
        self.client.force_login(self.staff)
        r = self.client.post(
            reverse("painel:item_toggle", args=[self.item.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("on", data)
        self.assertIn("disp", data["stats"])

    def test_toggle_exige_post(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse("painel:item_toggle", args=[self.item.pk]))
        self.assertEqual(r.status_code, 405)

    def test_toggle_encomenda(self):
        self.client.force_login(self.staff)
        self.assertTrue(self.item.encomendavel)
        r = self.client.post(reverse("painel:item_toggle_encomenda", args=[self.item.pk]))
        self.assertEqual(r.status_code, 302)
        self.item.refresh_from_db()
        self.assertFalse(self.item.encomendavel)

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

    def test_editar_ajax_get_form_e_post_linha(self):
        self.client.force_login(self.staff)
        r = self.client.get(
            reverse("painel:item_editar", args=[self.item.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        # Agora a resposta sao as celulas editaveis (edicao na linha), nao um <form>.
        self.assertIn(b"ed-cell", r.content)
        self.assertIn(b'name="nome"', r.content)
        r2 = self.client.post(
            reverse("painel:item_editar", args=[self.item.pk]),
            {"categoria": self.cat.pk, "nome": "Espresso Inline", "desc_pt": "",
             "desc_en": "", "preco": "7.00", "ordem": "0"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertTrue(data["ok"])
        self.assertIn("Espresso Inline", data["row"])


class AvaliacoesPainelTests(TestCase):
    def setUp(self):
        from cardapio.models import Avaliacao
        self.Avaliacao = Avaliacao
        self.av = Avaliacao.objects.create(autor="Joao", texto="Otimo", nota=5, fonte="google")
        U = get_user_model()
        self.staff = U.objects.create_user("dono", password="senha-forte-123", is_staff=True)

    def test_lista_exige_staff(self):
        r = self.client.get(reverse("painel:avaliacoes"))
        self.assertEqual(r.status_code, 302)

    def test_staff_lista_e_cria(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("painel:avaliacoes")).status_code, 200)
        r = self.client.post(
            reverse("painel:avaliacao_nova"),
            {"autor": "Ana", "texto": "Adorei", "nota": "5", "fonte": "tripadvisor", "ordem": "0", "aparece": "on"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(self.Avaliacao.objects.filter(autor="Ana").exists())

    def test_toggle_aparece(self):
        self.client.force_login(self.staff)
        self.assertTrue(self.av.aparece)
        r = self.client.post(reverse("painel:avaliacao_toggle", args=[self.av.pk]))
        self.assertEqual(r.status_code, 302)
        self.av.refresh_from_db()
        self.assertFalse(self.av.aparece)

    def test_editar_avaliacao_ajax(self):
        self.client.force_login(self.staff)
        r = self.client.get(
            reverse("painel:avaliacao_editar", args=[self.av.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        # Resposta = celulas editaveis da avaliacao (edicao na linha), sem <form>.
        self.assertIn(b"ed-cell", r.content)
        self.assertIn(b'name="autor"', r.content)
        r2 = self.client.post(
            reverse("painel:avaliacao_editar", args=[self.av.pk]),
            {"autor": "Joao Edit", "texto": "Otimo mesmo", "nota": "5",
             "fonte": "google", "ordem": "0", "aparece": "on"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r2.status_code, 200)
        self.assertIn("Joao Edit", r2.json()["row"])

    def test_landing_mostra_so_visiveis(self):
        self.Avaliacao.objects.create(autor="Oculto", texto="x", nota=5, fonte="outro", aparece=False)
        html = self.client.get(reverse("core:landing")).content.decode()
        self.assertIn("Joao", html)
        self.assertNotIn("Oculto", html)

    def test_sync_google_exige_post(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse("painel:avaliacoes_sync_google"))
        self.assertEqual(r.status_code, 405)

    def test_sync_google_sem_config_avisa_sem_crash(self):
        self.client.force_login(self.staff)
        with self.settings(GOOGLE_PLACES_API_KEY="", GOOGLE_PLACE_ID=""):
            r = self.client.post(reverse("painel:avaliacoes_sync_google"))
        self.assertEqual(r.status_code, 302)  # redireciona, sem rede/crash

    def test_botao_sync_so_aparece_quando_configurado(self):
        self.client.force_login(self.staff)
        with self.settings(GOOGLE_PLACES_API_KEY="", GOOGLE_PLACE_ID=""):
            html = self.client.get(reverse("painel:avaliacoes")).content.decode()
        self.assertNotIn("Sincronizar do Google", html)
        with self.settings(GOOGLE_PLACES_API_KEY="k", GOOGLE_PLACE_ID="p"):
            html2 = self.client.get(reverse("painel:avaliacoes")).content.decode()
        self.assertIn("Sincronizar do Google", html2)


class ConfiguracoesPainelTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.staff = U.objects.create_user("dono", password="senha-forte-123", is_staff=True)

    def test_salva_mapa_e_tripadvisor(self):
        from cardapio.models import ConfiguracaoSite
        self.client.force_login(self.staff)
        r = self.client.post(
            reverse("painel:configuracoes"),
            {"whatsapp": "5521999999999", "instagram": "maltomaia",
             "tripadvisor_url": "https://www.tripadvisor.com/x", "latitude": "-22.92", "longitude": "-42.25"},
        )
        self.assertEqual(r.status_code, 302)
        cfg = ConfiguracaoSite.get()
        self.assertTrue(cfg.tem_mapa)
        self.assertEqual(cfg.tripadvisor_url, "https://www.tripadvisor.com/x")


class FotoProdutoTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(slug="q", nome_pt="Quentes", ordem=0)
        self.item = Item.objects.create(
            categoria=self.cat, nome="Cappuccino", preco="12.00", destaque=True
        )
        U = get_user_model()
        self.staff = U.objects.create_user("dono", password="senha-forte-123", is_staff=True)

    def _imagem(self, cor=(200, 120, 60), tam=(40, 30)):
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        buff = BytesIO()
        Image.new("RGB", tam, cor).save(buff, format="PNG")
        return SimpleUploadedFile("foto.png", buff.getvalue(), content_type="image/png")

    def _editar(self, **extra):
        dados = {"categoria": self.cat.pk, "nome": self.item.nome, "desc_pt": "",
                 "desc_en": "", "preco": "12.00", "ordem": "0",
                 "disponivel": "on", "encomendavel": "on", "destaque": "on"}
        dados.update(extra)
        return self.client.post(
            reverse("painel:item_editar", args=[self.item.pk]), dados,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def test_upload_guarda_foto_como_jpeg(self):
        self.client.force_login(self.staff)
        r = self._editar(foto=self._imagem())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.item.refresh_from_db()
        self.assertTrue(self.item.tem_foto)
        self.assertEqual(self.item.foto_mime, "image/jpeg")
        self.assertEqual(bytes(self.item.foto)[:2], b"\xff\xd8")  # cabecalho JPEG

    def test_serve_foto_publica(self):
        self.client.force_login(self.staff)
        self._editar(foto=self._imagem())
        r = self.client.get(reverse("cardapio:item_foto", args=[self.item.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "image/jpeg")
        self.assertIn("max-age", r["Cache-Control"])

    def test_serve_404_sem_foto(self):
        r = self.client.get(reverse("cardapio:item_foto", args=[self.item.pk]))
        self.assertEqual(r.status_code, 404)

    def test_remover_foto(self):
        self.client.force_login(self.staff)
        self._editar(foto=self._imagem())
        self.item.refresh_from_db()
        self.assertTrue(self.item.tem_foto)
        self._editar(foto_clear="1")
        self.item.refresh_from_db()
        self.assertFalse(self.item.tem_foto)

    def test_menu_inclui_foto_url(self):
        from cardapio.services import menu_localizado
        self.client.force_login(self.staff)
        self._editar(foto=self._imagem())
        it = menu_localizado("pt")[0]["itens"][0]
        self.assertTrue(it["tem_foto"])
        self.assertIn(f"/item/{self.item.pk}/foto/", it["foto_url"])

    def test_imagem_invalida_nao_quebra(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_login(self.staff)
        ruim = SimpleUploadedFile("x.png", b"isto nao e imagem", content_type="image/png")
        r = self._editar(foto=ruim)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["ok"])  # erro_foto -> reabre o editor
        self.item.refresh_from_db()
        self.assertFalse(self.item.tem_foto)
