from django import forms

from .models import Recommendation
from movie.models import Entry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from prepareDB_utils import getOMDb
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field


class RecommendForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RecommendForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('const'), css_class='col-md-12'),
                Div(Field('nick'), css_class='col-md-9'),
                Div(Field('note'), css_class='col-md-12'),
            ),
        )
        self.helper.form_id = 'recommend_form'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-success'))
    const = forms.CharField(
        label='link or id',
        widget=forms.TextInput(attrs={'placeholder': 'eg. http://www.imdb.com/title/tt0111503/ or tt0111503'}),
        max_length=50,
    )
    nick = forms.CharField(
        label='nickname',
        max_length=30,
    )
    note = forms.CharField(
        label='note',
        max_length=120,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'an optional message (max 120 chars)', 'rows': 3}),
    )

    class Meta:
        model = Recommendation
        fields = ['const', 'nick', 'note']

    def clean_const(self):
        import re
        if Recommendation.objects.filter(date=timezone.now()).count() >= 5:
            raise forms.ValidationError('Today has been already recommended more than 5 titles')

        const = self.cleaned_data.get('const')
        find = re.search(r'tt\d{7}', const)
        if find:
            const = find.group(0)
            json = getOMDb(const)
            if not json:
                raise forms.ValidationError('Cant get data')
            elif json['Response'] == 'False':
                message = 'Title not found. '
                if 'Error' in json:
                    message += json['Error']
                raise forms.ValidationError(message)
            # try:
            #     imdb_votes = json['imdbVotes']
            #     votes = int(imdb_votes.replace(',', ''))
            #     rate = float(json['imdbRating'])
            #     if votes < 10000 or rate < 6:
            #         raise forms.ValidationError('Title must be rated 6 or better and have at least 10k ratings')
            # except:
            #     raise forms.ValidationError('Could not fetch votes ({}) or rating ({}) {}'.format(json['imdbVotes'], json['imdbRating']))

            if Entry.objects.filter(const=const).exists():
                obj = Entry.objects.get(const=const)
                raise forms.ValidationError(_(mark_safe(
                    '<a href="{}">{}</a> already exists. Check details <a href="{}">here</a>'.format(obj.url_imdb,
                                                                                    obj.name, obj.get_absolute_url()))))
            return const
        raise forms.ValidationError('Provide valid IMDb URL or just ID')
