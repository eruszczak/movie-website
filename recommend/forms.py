from django import forms
from common.prepareDB import get_title_or_create
from titles.models import Rating
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from datetime import date


class RecommendForm(forms.Form):
    const = forms.CharField(max_length=50)
    nick = forms.CharField(max_length=30, required=False)
    note = forms.CharField(max_length=120, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        self.recommended_for_user = kwargs.pop('recommendations', None)
        super(RecommendForm, self).__init__(*args, **kwargs)

    def clean(self):
        """check if daily limit is reached"""
        if self.recommended_for_user.filter(added_date__date=date.today()).count() >= 5:
            raise forms.ValidationError('Today has been already recommended more than 5 titles')

    def clean_const(self):
        """validate const and return title if for this user this can be recommended"""
        title = get_title_or_create(self.cleaned_data.get('const'))
        if not title:
            raise forms.ValidationError('Problem with getting data')
        if self.recommended_for_user.filter(title=title).exists()\
                or Rating.objects.filter(user=self.user, title=title).exists():
            raise forms.ValidationError(_(mark_safe(
                'This <a href="{}">title</a> has been already recommended or rated by this user.'.format(
                    title.get_absolute_url()))))
        return title

    def clean_nick(self):
        """nick is required if user is not logged else get request.user"""
        nick = self.cleaned_data.get('nick')
        if self.request.user.is_authenticated():
            return self.request.user, True
        if not nick:
            raise forms.ValidationError('If you are not logged, you must insert your nickname')
        return nick, False
