from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.forms import modelformset_factory, BaseModelFormSet
from django.utils.timezone import now

from shared.helpers import get_list_duplicates
from shared.widgets import MyRatingWidget, MyDateWidget
from titles.constants import TITLE_TYPE_CHOICES
from titles.models import Genre, Rating
from shared.forms import SearchFormMixin

User = get_user_model()


class TitleSearchForm(SearchFormMixin, forms.Form):
    year = forms.IntegerField(required=False)
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    keyword = forms.CharField(max_length=100, required=False, label='Keywords')
    genre = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.annotate(count=Count('title')).order_by('-count'), required=False)
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
        widgets = {
            'rate': MyRatingWidget,
            'rate_date': MyDateWidget
        }

    def __init__(self, user, title, from_formset=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.title = title
        self.from_formset = from_formset

    def save(self, commit=True):
        obj = super().save(False)
        obj.user = self.user
        obj.title = self.title
        obj.save()
        return obj

    def clean_rate(self):
        """rating must be integer 1-10"""
        rate = self.cleaned_data['rate']
        try:
            rate = int(rate)
        except (ValueError, TypeError):
            pass
        else:
            if 0 < rate < 11:
                return rate
        raise ValidationError(f'{rate} is not a value between 1-10')

    def clean_rate_date(self):
        rate_date = self.cleaned_data['rate_date']
        if rate_date > now().date():
            raise ValidationError(f'{rate_date} is a future date')

        # do not check rate_date uniqueness if form is part of a formset. Formset will walidate all dates at once
        if not self.from_formset and Rating.objects.exclude(
                pk=self.instance.pk).filter(user=self.user, title=self.title, rate_date=rate_date).exists():
            raise ValidationError(f'Another title was already rated on {rate_date}')

        return rate_date


class BaseRatingFormSet(BaseModelFormSet):
    def __init__(self, user, title, *args, **kwargs):
        self.user = user
        self.title = title
        kwargs['queryset'] = Rating.objects.filter(title=title, user=user).order_by('-rate_date')
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        RateForm has rate_date validation (it checks eg. before new Rating is created,
        if the title was already rated by the user on the same day).
        In formset I want to validate uniqueness of rate_dates at once.
        Because if Rating from May 15 will be changed, another rating couldn't be set to May 15.
        """
        super().clean()
        dates = [f.cleaned_data['rate_date'] for f in self.forms if f.cleaned_data and f.cleaned_data.get('rate_date') and not f.cleaned_data.get('DELETE')]
        duplicates = get_list_duplicates(dates)
        if len(duplicates):
            duplicates = [d.strftime('%Y-%m-%d') for d in duplicates]
            raise ValidationError(f"Dates: {', '.join(duplicates)} are not unique.")

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs.update({
            'user': self.user,
            'title': self.title,
            'from_formset': True
        })
        return kwargs


RatingFormset = modelformset_factory(
    Rating, form=RateForm, formset=BaseRatingFormSet, extra=3, can_delete=True, max_num=100
)
