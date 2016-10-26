from django import forms
from .models import Title
from datetime import datetime


class EditRating(forms.ModelForm):
    rate_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2013, datetime.now().year + 1)), required=False)      # todo
    rate = forms.ChoiceField(choices=((n, n) for n in range(1, 11)), required=False)

    class Meta:
        model = Title
        fields = ('rate', 'rate_date')
