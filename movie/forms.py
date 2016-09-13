from django import forms
from .models import Entry


class EditEntry(forms.ModelForm):
    rate_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    rate = forms.ChoiceField(choices=((n, n) for n in range(1, 11)), required=False)
    class Meta:
        model = Entry
        fields = ('rate', 'rate_date')
