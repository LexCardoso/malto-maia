from django import forms

from cardapio.models import Item

_INPUT = "adm-input"


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "categoria", "nome", "desc_pt", "desc_en",
            "preco", "destaque", "disponivel", "ordem",
        ]
        widgets = {
            "categoria": forms.Select(attrs={"class": _INPUT}),
            "nome": forms.TextInput(attrs={"class": _INPUT}),
            "desc_pt": forms.TextInput(attrs={"class": _INPUT}),
            "desc_en": forms.TextInput(attrs={"class": _INPUT}),
            "preco": forms.NumberInput(attrs={"class": _INPUT, "step": "0.01", "min": "0", "placeholder": "a definir"}),
            "ordem": forms.NumberInput(attrs={"class": _INPUT, "min": "0"}),
        }

    def clean_preco(self):
        preco = self.cleaned_data.get("preco")
        if preco is not None and preco < 0:
            raise forms.ValidationError("Preço não pode ser negativo.")
        return preco
