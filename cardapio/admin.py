from django.contrib import admin

from .models import Categoria, ConfiguracaoSite, Item


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ("nome", "preco", "destaque", "disponivel", "ordem")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome_pt", "slug", "ordem")
    list_editable = ("ordem",)
    prepopulated_fields = {"slug": ("nome_pt",)}
    inlines = [ItemInline]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "preco", "destaque", "disponivel")
    list_filter = ("categoria", "destaque", "disponivel")
    list_editable = ("preco", "destaque", "disponivel")
    search_fields = ("nome", "desc_pt", "desc_en")


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "cardapio_atualizado_em", "whatsapp", "instagram")

    def has_add_permission(self, request):
        return not ConfiguracaoSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
