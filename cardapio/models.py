"""Modelos do cardapio — single-tenant (uma cafeteria).

Categoria 1--N Item. Preco null = "a definir". Conteudo bilingue PT/EN nos
campos *_pt / *_en (nome do item nao traduz, so a descricao).
"""
from django.db import models
from django.utils import timezone


def _limpa_cache_conteudo():
    """Invalida o cache dos overrides de texto/foto do site (apos editar no painel)."""
    from django.core.cache import cache
    cache.delete_many(["textos_site", "fotos_site_map"])


class Categoria(models.Model):
    slug = models.SlugField(max_length=40, unique=True)
    nome_pt = models.CharField("nome (PT)", max_length=80)
    nome_en = models.CharField("nome (EN)", max_length=80, blank=True)
    nota_pt = models.CharField("nota (PT)", max_length=200, blank=True)
    nota_en = models.CharField("nota (EN)", max_length=200, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nome_pt

    def nome(self, lang="pt"):
        return self.nome_en if lang == "en" and self.nome_en else self.nome_pt

    def nota(self, lang="pt"):
        return self.nota_en if lang == "en" and self.nota_en else self.nota_pt


class Item(models.Model):
    categoria = models.ForeignKey(
        Categoria, related_name="itens", on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=120)
    desc_pt = models.CharField("descrição (PT)", max_length=300, blank=True)
    desc_en = models.CharField("descrição (EN)", max_length=300, blank=True)
    preco = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Deixe vazio para 'a definir'.",
    )
    destaque = models.BooleanField("carro-chefe", default=False)
    disponivel = models.BooleanField(default=True)
    encomendavel = models.BooleanField(
        "aparece na encomenda", default=True,
        help_text="Desligado: some da página de Encomenda (mas continua no cardápio).",
    )
    # Foto do produto guardada NO BANCO (Render free nao tem disco persistente).
    # Os bytes ja entram redimensionados/comprimidos (ver painel._salvar_foto).
    foto = models.BinaryField(null=True, blank=True, editable=False)
    foto_mime = models.CharField(max_length=60, blank=True, default="")
    ordem = models.PositiveIntegerField(default=0)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["categoria__ordem", "ordem", "id"]
        verbose_name = "item"
        verbose_name_plural = "itens"

    def __str__(self):
        return self.nome

    def desc(self, lang="pt"):
        return self.desc_en if lang == "en" and self.desc_en else self.desc_pt

    @property
    def tem_foto(self):
        """True se o item tem foto — checa o mime (barato), sem carregar os bytes."""
        return bool(self.foto_mime)


class ConfiguracaoSite(models.Model):
    """Singleton (pk=1): data de atualizacao do cardapio + contatos."""

    cardapio_atualizado_em = models.DateField(default=timezone.now)
    whatsapp = models.CharField(max_length=20, blank=True)
    instagram = models.CharField(max_length=40, blank=True)
    tripadvisor_url = models.URLField("TripAdvisor (link)", blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        verbose_name = "configuração do site"
        verbose_name_plural = "configuração do site"

    def __str__(self):
        return "Configuração do site"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def marcar_atualizado_hoje(self):
        self.cardapio_atualizado_em = timezone.localdate()
        self.save(update_fields=["cardapio_atualizado_em"])

    @property
    def tem_mapa(self):
        return self.latitude is not None and self.longitude is not None


class Avaliacao(models.Model):
    """Avaliacao curada pelo dono (Google/TripAdvisor/outro) — ele escolhe quais aparecem."""

    FONTES = [("google", "Google"), ("tripadvisor", "TripAdvisor"), ("outro", "Outro")]

    autor = models.CharField(max_length=80)
    texto = models.TextField()
    nota = models.PositiveSmallIntegerField("nota (1-5)", default=5)
    fonte = models.CharField(max_length=20, choices=FONTES, default="google")
    ref = models.CharField(
        "ref. externa", max_length=300, blank=True, default="",
        help_text="ID da avaliação na fonte (ex.: Google) — usado pelo sync p/ não duplicar.",
    )
    aparece = models.BooleanField("aparece no site", default=True)
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordem", "-criado_em"]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"

    def __str__(self):
        return f"{self.autor} ({self.get_fonte_display()})"

    @property
    def estrelas(self):
        n = max(0, min(5, int(self.nota)))
        return "★" * n + "☆" * (5 - n)


class TextoSite(models.Model):
    """Override editavel de uma string de UI (core/i18n.py STRINGS).

    O dono edita pelo painel; o tag {% t %} usa o valor daqui se existir, senao
    cai no i18n. Vazio nos dois idiomas = volta a usar o i18n.
    """

    chave = models.CharField(max_length=60, unique=True)
    pt = models.TextField(blank=True)
    en = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "texto do site"
        verbose_name_plural = "textos do site"

    def __str__(self):
        return self.chave

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _limpa_cache_conteudo()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        _limpa_cache_conteudo()


class FotoSite(models.Model):
    """Foto do site (hero, fachada, galeria, Visite, Conceito, Instagram...) trocada
    pelo dono. Guardada NO BANCO como bytes. Vazio = usa o estatico padrao do slot."""

    slug = models.SlugField(max_length=40, unique=True)
    foto = models.BinaryField(null=True, blank=True, editable=False)
    foto_mime = models.CharField(max_length=60, blank=True, default="")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "foto do site"
        verbose_name_plural = "fotos do site"

    def __str__(self):
        return self.slug

    @property
    def tem_foto(self):
        return bool(self.foto_mime)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _limpa_cache_conteudo()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        _limpa_cache_conteudo()
