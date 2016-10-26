from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field
from django import forms

from .models import Recommendation


class RecommendForm(forms.ModelForm):
    const = forms.CharField()
    nick = forms.CharField()
    note = forms.CharField()

    class Meta:
        model = Recommendation
        fields = ('const', 'nick', 'note')
    # def clean_const(self):
    #     if Recommendation.objects.filter(date=timezone.now()).count() >= 5:
    #         raise forms.ValidationError('Today has been already recommended more than 5 titles')
    #
    #     const = self.cleaned_data.get('const')
    #     find = re.search(r'tt\d{7}', const)
    #     if find:
    #         const = find.group(0)
    #         json = get_omdb(const)
    #         if not json:
    #             raise forms.ValidationError('Cant get data')
    #         elif json['Response'] == 'False':
    #             message = 'Title not found. '
    #             if 'Error' in json:
    #                 message += json['Error']
    #             raise forms.ValidationError(message)
    #         # try:
    #         #     imdb_votes = json['imdbVotes']
    #         #     votes = int(imdb_votes.replace(',', ''))
    #         #     rate = float(json['imdbRating'])
    #         #     if votes < 10000 or rate < 6:
    #         #         raise forms.ValidationError('Title must be rated 6 or better and have at least 10k ratings')
    #         # except:
    #         #     raise forms.ValidationError('Could not fetch votes ({}) or rating ({}) {}'.format(json['imdbVotes'], json['imdbRating']))
    #
    #         if Entry.objects.filter(const=const).exists():
    #             obj = Entry.objects.get(const=const)
    #             raise forms.ValidationError(_(mark_safe(
    #                 '<a href="{}">{}</a> already exists. Check details <a href="{}">here</a>'.format(obj.url_imdb,
    #                                                                                 obj.name, obj.get_absolute_url()))))
    #         return const
    #     raise forms.ValidationError('Provide valid IMDb URL or just ID')
