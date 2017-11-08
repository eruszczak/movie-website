from django import forms

from movie.models import Title
from movie.shared import SearchFormMixin


class TitleSearchForm(SearchFormMixin, forms.ModelForm):

    class Meta:
        model = Title
        fields = '__all__'