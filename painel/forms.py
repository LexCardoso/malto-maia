from django import forms

from cardapio.models import Avaliacao, ConfiguracaoSite, Item

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


class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSite
        fields = ["whatsapp", "instagram", "tripadvisor_url", "latitude", "longitude"]
        widgets = {
            "whatsapp": forms.TextInput(attrs={"class": _INPUT, "placeholder": "5522999999999"}),
            "instagram": forms.TextInput(attrs={"class": _INPUT, "placeholder": "doceria_maltomaia"}),
            "tripadvisor_url": forms.URLInput(attrs={"class": _INPUT, "placeholder": "https://www.tripadvisor.com.br/..."}),
            "latitude": forms.NumberInput(attrs={"class": _INPUT, "step": "any", "placeholder": "-22.9226"}),
            "longitude": forms.NumberInput(attrs={"class": _INPUT, "step": "any", "placeholder": "-42.2519"}),
        }


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ["autor", "texto", "nota", "fonte", "aparece", "ordem"]
        widgets = {
            "autor": forms.TextInput(attrs={"class": _INPUT}),
            "texto": forms.Textarea(attrs={"class": _INPUT, "rows": 3}),
            "nota": forms.NumberInput(attrs={"class": _INPUT, "min": "1", "max": "5"}),
            "fonte": forms.Select(attrs={"class": _INPUT}),
            "ordem": forms.NumberInput(attrs={"class": _INPUT, "min": "0"}),
        }
