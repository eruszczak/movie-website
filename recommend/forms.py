from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.models import UserFollow
from common.prepareDB import get_title_or_create
from recommend.models import Recommendation
from titles.models import Rating
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from datetime import date


User = get_user_model()


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


class RecommendTitleForm(forms.ModelForm):
    user = forms.ModelMultipleChoiceField(queryset=User.objects.none())

    class Meta:
        model = Recommendation
        fields = ('user', 'sender', 'title')

    def __init__(self, user, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(
            pk__in=UserFollow.objects.filter(follower=user).exclude(
                Q(followed__rating__title=title) | Q(followed__recommendation__title=title)
        ).values_list('followed__pk', flat=True))

        # self.fields['user'].queryset = User.objects.filter(userfollow__follower=user).exclude(
            # Q(userfollow__followed__rating__title=title) |
            # Q(userfollow__followed__recommendation__title=title)
        # ).distinct()
        print(self.fields['user'].queryset)
        #.select_related('userfollow__followed')

        print(
            UserFollow.objects.filter(follower=user).exclude(
                    Q(followed__rating__title=title) | Q(followed__recommendation__title=title)
        ).values_list('followed__pk', flat=True)
        )