from django import forms
from .models import Recommendation
import re
from django.utils import timezone
from common.prepareDB import get_title_or_create


class RecommendForm(forms.Form):
    const = forms.CharField(max_length=50)
    nick = forms.CharField(max_length=30, required=False)
    note = forms.CharField(max_length=120, required=False)

    # class Meta:
    #     model = Recommendation
    #     fields = ('const', 'nick', 'note')
    def clean_const(self):
        # if Recommendation.objects.filter(date=timezone.now()).count() >= 5:
        #     raise forms.ValidationError('Today has been already recommended more than 5 titles')

        const = self.cleaned_data.get('const')
        print(const)
        title = get_title_or_create(const)
        if not title:
            raise forms.ValidationError('Cant get data')

        # if Recommend.objects.filter(const=const).exists():
        #     obj = Entry.objects.get(const=const)
        #     raise forms.ValidationError(_(mark_safe(
        #         '<a href="{}">{}</a> already exists. Check details <a href="{}">here</a>'.format(obj.url_imdb,
        #                                                                         obj.name, obj.get_absolute_url()))))
        return title
