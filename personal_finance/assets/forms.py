from django import forms

from .models import Asset, Portfolio, Holding


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
            "symbol": forms.TextInput(attrs={"placeholder": "e.g., AAPL"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g., Apple Inc."}),
            "currency": forms.TextInput(attrs={"placeholder": "e.g., USD"}),
            "exchange": forms.TextInput(attrs={"placeholder": "e.g., NASDAQ"}),
        }


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            "name",
            "description",
            "is_default",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "name": forms.TextInput(attrs={"placeholder": "e.g., My Main Portfolio"}),
        }


class HoldingForm(forms.ModelForm):
    class Meta:
        model = Holding
        fields = [
            "asset",
            "portfolio",
            "quantity",
            "average_price",
            "currency",
            "acquired_at",
            "in_portfolio",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "acquired_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "quantity": forms.NumberInput(attrs={"step": "0.00000001"}),
            "average_price": forms.NumberInput(attrs={"step": "0.01"}),
        }
