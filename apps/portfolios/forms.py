from django import forms

from apps.assets.models import Asset, Exchange

from .models import Portfolio, Transaction


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description", "is_default"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class TransactionForm(forms.ModelForm):
    """A transaction entered by ticker; the asset is created on first use."""

    ticker = forms.CharField(max_length=20, help_text="For example PETR4, HGLG11 or AAPL.")
    exchange = forms.ChoiceField(choices=Exchange.choices, initial=Exchange.B3)

    class Meta:
        model = Transaction
        fields = [
            "portfolio", "kind", "trade_date", "ticker", "exchange",
            "quantity", "price", "fees", "amount", "broker", "notes",
        ]  # fmt: skip
        widgets = {
            "trade_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["portfolio"].queryset = Portfolio.objects.filter(user=user)
        if self.instance.pk:
            self.fields["ticker"].initial = self.instance.asset.ticker
            self.fields["exchange"].initial = self.instance.asset.exchange

    def clean_ticker(self) -> str:
        ticker = self.cleaned_data["ticker"].strip().upper()
        Asset.ticker.field.run_validators(ticker)
        return ticker

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("ticker") and cleaned.get("exchange") and not self.errors:
            # Only reached with a valid form, so no stray asset is created.
            self.instance.asset, _ = Asset.get_or_create_for_ticker(
                cleaned["ticker"], cleaned["exchange"]
            )
        return cleaned
