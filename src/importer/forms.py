from django import forms

from shared.forms import SizeExtValidatorMixin


class ImportRatingsForm(SizeExtValidatorMixin, forms.Form):
    csv_file = forms.FileField(label='', required=True)

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        self.validate_extension(file.name, ['.csv'])
        self.validate_size(file.size, 2000)
        return file
