"""Template tags/filters da Malto Maia: tradução de UI e preço em BRL."""
from decimal import Decimal, InvalidOperation

from django import template

from core.i18n import t as _t

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    """{% t "hero.title" %} -> string no idioma atual."""
    request = context.get("request")
    lang = getattr(request, "LANG", "pt") if request else "pt"
    return _t(key, lang)


@register.filter
def brl(value):
    """Decimal/float -> 'R$ 1.234,56'. Vazio se None."""
    if value is None or value == "":
        return ""
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return ""
    s = f"{v:,.2f}"  # estilo en-US: 1,234.56
    s = s.replace(",", "_").replace(".", ",").replace("_", ".")  # -> 1.234,56
    return f"R$ {s}"


@register.filter
def nl2br_lines(value):
    """Quebra '\\n' em lista de linhas (titulo do hero com quebra)."""
    if not value:
        return []
    return value.split("\n")
