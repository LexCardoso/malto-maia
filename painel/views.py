"""Painel do admin (dono) — editar o cardapio que aparece no site.

Acesso restrito a usuarios staff. Login com django-axes (anti-bruteforce).
"""
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cardapio.models import Categoria, ConfiguracaoSite, Item

from .forms import ItemForm

staff_required = user_passes_test(
    lambda u: u.is_active and u.is_staff, login_url="painel:login"
)


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
    messages.success(
        request,
        f"“{item.nome}” marcado como {'disponível' if item.disponivel else 'indisponível'}.",
    )
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
