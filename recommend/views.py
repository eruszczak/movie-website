from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils import timezone

# from utils.prepareDB import get_title_or_create
from .forms import RecommendForm
from .models import Recommendation


def recommend(request, username):
    is_owner = username == request.user.username
    user = User.objects.get(username=username)
    recommended_for_user = Recommendation.objects.filter(user=user)
    form = RecommendForm(initial={'nick': request.user.username})
    if request.method == 'POST':
        form = RecommendForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.user:
                instance.sender = request.user
            else:
                instance.nick = None
            instance.user = user
            # instance.title = get_title_or_create(instance.const)
            instance.save()
            # messages.success(request, 'added recommendation', extra_tags='alert-success')
            return redirect(reverse("recommend"))
    recommended_today = recommended_for_user.filter(added_date=timezone.now())
    context = {
        'obj_list': recommended_for_user,
        'form': form,
        'count': {
            # 'today': recommended_today,
            # 'today2': recommended_today * 2,
            # 'active_recommendations': Recommendation.objects.filter(user=request.user).count(),
        },
    }
    return render(request, 'recommend/home.html', context)
