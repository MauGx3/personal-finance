from django import forms
from django.conf import settings

from apps.portfolios.models import Portfolio

from .services import available_parsers


class ImportForm(forms.Form):
    portfolio = forms.ModelChoiceField(queryset=Portfolio.objects.none())
    file = forms.FileField(help_text="A .xlsx or .csv export. Re-importing a file is safe.")
    parser = forms.ChoiceField(required=False, label="Format")
    dry_run = forms.BooleanField(
        required=False,
        label="Preview only",
        help_text="Report what would be imported, save nothing.",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["portfolio"].queryset = Portfolio.objects.filter(user=user)
        self.fields["portfolio"].initial = Portfolio.default_for(user)
        self.fields["parser"].choices = [("", "Detect automatically")] + [
            (parser.name, parser.label) for parser in available_parsers()
        ]

    def clean_file(self):
        upload = self.cleaned_data["file"]
        if upload.size > settings.IMPORT_MAX_UPLOAD_BYTES:
            raise forms.ValidationError("The file is larger than 10 MB.")
        return upload
