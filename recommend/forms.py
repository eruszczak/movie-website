from django import forms

from .models import Recommendation
from movie.models import Entry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from prepareDB_utils import getOMDb


class RecommendForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['const', 'nick', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'cols': 30, 'rows': 3, 'placeholder': 'an optional message (max 120 chars)'}),
            'const': forms.TextInput(attrs={'placeholder': 'eg. http://www.imdb.com/title/tt0111503/ or tt0111503'}),
            'nick': forms.TextInput(attrs={'placeholder': 'nickname'}),
        }
        labels = {
            'const': _('IMDb URL/ID'),
            'nick': _('Nickname'),
        }

    def clean_const(self):
        import re
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
            if Recommendation.objects.filter(date=timezone.now()).count() >= 5:
                raise forms.ValidationError('Today has been already recommended more than 5 titles')
            return const
        raise forms.ValidationError('Provide valid IMDb URL or just ID')
