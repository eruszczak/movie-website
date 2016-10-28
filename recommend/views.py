from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecommendForm
from .models import Recommendation
from movie.models import Rating
from django import forms
from datetime import date


def recommend(request, username):
    user = User.objects.get(username=username)
    recommended_for_user = Recommendation.objects.filter(user=user)
    form = RecommendForm()
    if request.method == 'POST':
        # form = RecommendForm(request.POST)
        form = RecommendForm(request.POST)
        print(form.errors)
        if form.is_valid():
            instance = Recommendation()
            instance.title = form.cleaned_data.get('const')

            if recommended_for_user.filter(added_date__date=date.today()).count() > 5:
                raise forms.ValidationError('This user already got 5 recommendations today. Wait until tomorrow.')
            if recommended_for_user.filter(title=instance.title).exists() or Rating.objects.filter(user=user, title=instance.title):
                raise forms.ValidationError('This title has been already recommended or rated by this user.')

            if request.user.is_authenticated():
                instance.sender = request.user
            else:
                instance.nick = form.cleaned_data.get('nick')
            instance.user = user
            instance.note = form.cleaned_data.get('note')
            instance.save()
            messages.success(request, 'added recommendation', extra_tags='alert-success')
            print(instance)
            return redirect(reverse("recommend", kwargs={'username': username}))
    # recommended_today = recommended_for_user.filter(added_date=timezone.now())
    context = {
        'obj_list': recommended_for_user,
        'form': form,
        # 'count': {
            # 'today': recommended_today,
            # 'today2': recommended_today * 2,
            # 'active_recommendations': Recommendation.objects.filter(user=request.user).count(),
        # },
        'is_owner': user == request.user,
    }
    return render(request, 'recommend/home.html', context)
