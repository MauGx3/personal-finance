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
            "metadata": forms.Textarea(attrs={"rows": 3, "placeholder": "Additional metadata in JSON format"}),
            "symbol": forms.TextInput(attrs={"placeholder": "e.g., AAPL"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g., Apple Inc."}),
            "currency": forms.TextInput(attrs={"placeholder": "e.g., USD"}),
            "exchange": forms.TextInput(attrs={"placeholder": "e.g., NASDAQ"}),
            "isin": forms.TextInput(attrs={"placeholder": "e.g., US0378331005"}),
            "cusip": forms.TextInput(attrs={"placeholder": "e.g., 037833100"}),
        }
        labels = {
            "asset_type": "Asset Type",
            "isin": "ISIN Code",
            "cusip": "CUSIP Code",
            "is_active": "Currently Active",
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
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional description of this portfolio"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g., My Main Portfolio"}),
        }
        labels = {
            "is_default": "Set as Default Portfolio",
        }
        help_texts = {
            "is_default": "Only one portfolio can be marked as default.",
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
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional notes about this holding"}),
            "acquired_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "quantity": forms.NumberInput(attrs={"step": "0.00000001", "placeholder": "0.00000001"}),
            "average_price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "currency": forms.TextInput(attrs={"placeholder": "e.g., USD"}),
        }
        labels = {
            "average_price": "Average Purchase Price",
            "acquired_at": "Date Acquired",
            "in_portfolio": "Include in Portfolio Calculations",
        }
        help_texts = {
            "portfolio": "Leave blank to keep holding outside of any portfolio.",
            "in_portfolio": "Uncheck to exclude this holding from portfolio calculations.",
        }
