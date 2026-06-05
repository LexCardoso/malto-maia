"""Painel do admin (dono) — editar o cardapio que aparece no site.

Acesso restrito a usuarios staff. Login com django-axes (anti-bruteforce).
"""
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cardapio.models import Avaliacao, Categoria, ConfiguracaoSite, Item

from .forms import AvaliacaoForm, ConfiguracaoForm, ItemForm

staff_required = user_passes_test(
    lambda u: u.is_active and u.is_staff, login_url="painel:login"
)


def _ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


class PainelLoginView(LoginView):
    template_name = "painel/login.html"
    redirect_authenticated_user = True


@staff_required
def dashboard(request):
    busca = request.GET.get("q", "").strip()
    itens = Item.objects.select_related("categoria").all()
    if busca:
        itens = itens.filter(nome__icontains=busca)
    return render(
        request,
        "painel/dashboard.html",
        {
            "itens": itens,
            "n_total": Item.objects.count(),
            "n_disp": Item.objects.filter(disponivel=True).count(),
            "n_indisp": Item.objects.filter(disponivel=False).count(),
            "n_tbd": Item.objects.filter(preco__isnull=True).count(),
            "n_encomenda": Item.objects.filter(encomendavel=True).count(),
            "n_cat": Categoria.objects.count(),
            "config": ConfiguracaoSite.get(),
            "busca": busca,
        },
    )


@staff_required
def item_novo(request):
    form = ItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        ConfiguracaoSite.get().marcar_atualizado_hoje()
        messages.success(request, "Item adicionado.")
        return redirect("painel:dashboard")
    return render(request, "painel/item_form.html", {"form": form, "novo": True})


@staff_required
def item_editar(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        ConfiguracaoSite.get().marcar_atualizado_hoje()
        messages.success(request, "Item atualizado.")
        return redirect("painel:dashboard")
    return render(
        request, "painel/item_form.html", {"form": form, "item": item, "novo": False}
    )


@require_POST
@staff_required
def item_toggle(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.disponivel = not item.disponivel
    item.save(update_fields=["disponivel", "atualizado_em"])
    ConfiguracaoSite.get().marcar_atualizado_hoje()
    if _ajax(request):
        return JsonResponse({"on": item.disponivel, "stats": {
            "disp": Item.objects.filter(disponivel=True).count(),
            "indisp": Item.objects.filter(disponivel=False).count(),
        }})
    messages.success(
        request,
        f"“{item.nome}” marcado como {'disponível' if item.disponivel else 'indisponível'}.",
    )
    return redirect("painel:dashboard")


@require_POST
@staff_required
def item_toggle_encomenda(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.encomendavel = not item.encomendavel
    item.save(update_fields=["encomendavel", "atualizado_em"])
    if _ajax(request):
        return JsonResponse({"on": item.encomendavel, "stats": {
            "enc": Item.objects.filter(encomendavel=True).count(),
        }})
    estado = "entra na" if item.encomendavel else "saiu da"
    messages.success(request, f"“{item.nome}” {estado} encomenda.")
    return redirect("painel:dashboard")


@require_POST
@staff_required
def item_excluir(request, pk):
    item = get_object_or_404(Item, pk=pk)
    nome = item.nome
    item.delete()
    ConfiguracaoSite.get().marcar_atualizado_hoje()
    messages.success(request, f"“{nome}” removido.")
    return redirect("painel:dashboard")


@require_POST
@staff_required
def marcar_atualizado(request):
    ConfiguracaoSite.get().marcar_atualizado_hoje()
    messages.success(request, "Data de atualização marcada para hoje.")
    return redirect("painel:dashboard")


# ── Configuracoes do site (TripAdvisor, Instagram, mapa) ──
@staff_required
def configuracoes(request):
    config = ConfiguracaoSite.get()
    form = ConfiguracaoForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Configurações salvas.")
        return redirect("painel:configuracoes")
    return render(request, "painel/configuracoes.html", {"form": form, "config": config})


# ── Avaliacoes (curadoria — o dono escolhe quais aparecem) ──
@staff_required
def avaliacoes(request):
    from cardapio.reviews_google import esta_configurado

    return render(
        request,
        "painel/avaliacoes.html",
        {
            "avaliacoes": Avaliacao.objects.all(),
            "n_visiveis": Avaliacao.objects.filter(aparece=True).count(),
            "google_pronto": esta_configurado(),
        },
    )


@require_POST
@staff_required
def avaliacoes_sync_google(request):
    """Puxa as avaliacoes do Google como rascunho; o dono liga quais aparecem."""
    from cardapio.reviews_google import (
        GoogleReviewsError,
        esta_configurado,
        sincronizar_google,
    )

    if not esta_configurado():
        messages.error(
            request,
            "Sincronização do Google ainda não configurada (faltam a chave e o Place ID).",
        )
        return redirect("painel:avaliacoes")
    try:
        r = sincronizar_google()
    except GoogleReviewsError as e:
        messages.error(request, f"Não consegui sincronizar com o Google: {e}")
        return redirect("painel:avaliacoes")
    messages.success(
        request,
        f"Google: {r['encontradas']} avaliações lidas — {r['criadas']} novas (como "
        f"rascunho), {r['atualizadas']} atualizadas. Clique em “Mostrar” nas que quiser "
        "no site.",
    )
    return redirect("painel:avaliacoes")


@staff_required
def avaliacao_nova(request):
    form = AvaliacaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Avaliação adicionada.")
        return redirect("painel:avaliacoes")
    return render(request, "painel/avaliacao_form.html", {"form": form, "novo": True})


@staff_required
def avaliacao_editar(request, pk):
    av = get_object_or_404(Avaliacao, pk=pk)
    form = AvaliacaoForm(request.POST or None, instance=av)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Avaliação atualizada.")
        return redirect("painel:avaliacoes")
    return render(request, "painel/avaliacao_form.html", {"form": form, "av": av, "novo": False})


@require_POST
@staff_required
def avaliacao_toggle(request, pk):
    av = get_object_or_404(Avaliacao, pk=pk)
    av.aparece = not av.aparece
    av.save(update_fields=["aparece"])
    if _ajax(request):
        return JsonResponse({"on": av.aparece, "stats": {
            "vis": Avaliacao.objects.filter(aparece=True).count(),
        }})
    estado = "aparece" if av.aparece else "está oculta"
    messages.success(request, f"Avaliação de “{av.autor}” {estado} no site.")
    return redirect("painel:avaliacoes")


@require_POST
@staff_required
def avaliacao_excluir(request, pk):
    av = get_object_or_404(Avaliacao, pk=pk)
    autor = av.autor
    av.delete()
    messages.success(request, f"Avaliação de “{autor}” removida.")
    return redirect("painel:avaliacoes")
