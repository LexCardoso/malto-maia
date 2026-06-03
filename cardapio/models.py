"""Modelos do cardapio — single-tenant (uma cafeteria).

Categoria 1--N Item. Preco null = "a definir". Conteudo bilingue PT/EN nos
campos *_pt / *_en (nome do item nao traduz, so a descricao).
"""
from django.db import models
from django.utils import timezone


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


class ConfiguracaoSite(models.Model):
    """Singleton (pk=1): data de atualizacao do cardapio + contatos."""

    cardapio_atualizado_em = models.DateField(default=timezone.now)
    whatsapp = models.CharField(max_length=20, blank=True)
    instagram = models.CharField(max_length=40, blank=True)

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
