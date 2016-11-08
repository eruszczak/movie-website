from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecommendForm
from .models import Recommendation
from movie.models import Rating
from django.forms import ValidationError
from datetime import date


def recommend(request, username):
    user = User.objects.get(username=username)
    recommended_for_user = Recommendation.objects.filter(user=user)
    recommended_today = recommended_for_user.filter(added_date__date=date.today()).count()
    if request.method == 'POST':
        if request.POST.get('delete_recommend'):
            to_del = Recommendation.objects.filter(pk=request.POST.get('recommend_pk'), user=request.user).first()
            if to_del.is_active():
                to_del.delete()
                messages.info(request, '')
            return redirect(user.userprofile.recommend_url())
        form = RecommendForm(request.POST)
        if form.is_valid():
            instance = Recommendation()
            instance.title = form.cleaned_data.get('const')
            if recommended_today > 5:
                raise ValidationError('This user already got 5 recommendations today. Wait until tomorrow.')
            if recommended_for_user.filter(title=instance.title).exists() or Rating.objects.filter(user=user, title=instance.title).exists():
                raise ValidationError('This title has been already recommended or rated by this user.')
            if request.user.is_authenticated():
                instance.sender = request.user
            else:
                instance.nick = form.cleaned_data.get('nick')
                if not instance.nick:
                    raise ValidationError('Not logged users have to fill nick nickname.')
            instance.user = user
            instance.note = form.cleaned_data.get('note')
            instance.save()
            messages.success(request, 'added recommendation', extra_tags='alert-success')
            return redirect(user.userprofile.recommend_url())
    else:
        form = RecommendForm()
    context = {
        'obj_list': recommended_for_user,
        'form': form,
        'count': {
            'today': recommended_today,
            'active_recommendations': len([x for x in recommended_for_user if x.is_active]),
        },
        'is_owner': user == request.user,
    }
    return render(request, 'recommend.html', context)
