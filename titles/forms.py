import re

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.forms import inlineformset_factory, modelformset_factory, BaseModelFormSet

from shared.widgets import MySelectMultipleWidget
from titles.constants import TITLE_TYPE_CHOICES
from titles.models import Title, Genre, Rating
from shared.forms import SearchFormMixin


User = get_user_model()


class TitleSearchForm(SearchFormMixin, forms.Form):
    year = forms.IntegerField(required=False)
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    keyword = forms.CharField(max_length=100, required=False, label='Keywords')
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.annotate(count=Count('title')).order_by('-count'), required=False)
    type = forms.ChoiceField(choices=TITLE_TYPE_CHOICES, required=False)

    @staticmethod
    def search_keyword(value):
        if len(value) > 2:
            return Q(name__icontains=value)
        return Q(name__istartswith=value)

    @staticmethod
    def search_genre(value):
        return Q(genres__in=value)

    @staticmethod
    def search_year(value):
        return Q(release_date__year=value)

    @staticmethod
    def search_type(value):
        return Q(type=value)

    @staticmethod
    def search_user(value):
        return Q(rating__user=value)


class RateForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ('rate_date', 'rate')


class BaseRatingFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.queryset = Rating.objects.filter(title=None, user=None)


RatingFormset = modelformset_factory(
    Rating, form=RateForm, formset=BaseRatingFormSet, extra=3, can_delete=True, max_num=100
)
