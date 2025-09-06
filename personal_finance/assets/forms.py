from django import forms

from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "symbol",
            "name",
            "asset_type",
            "currency",
            "exchange",
            "isin",
            "cusip",
            "metadata",
            "is_active",
        ]
        widgets = {
            "metadata": forms.Textarea(attrs={"rows": 3}),
        }
