from django import forms
from django.db.models import Q, Count

from movie.models import Title, Genre
from movie.shared import SearchFormMixin


class TitleSearchForm(SearchFormMixin, forms.Form):
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.annotate(num=Count('title')).order_by('-num'))

    @staticmethod
    def search_genre(value):
        print(value)
        return Q()