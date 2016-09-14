from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from .forms import RecommendForm
from .models import Recommendation

from prepareDB_utils import getOMDb
from django.contrib import messages
from django.utils import timezone


def recommend(request):
    form = RecommendForm(initial={'nick': request.user.username})
    if request.method == 'POST':
        form = RecommendForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            json = getOMDb(instance.const)
            if json:
                instance.name = json['Title']
                instance.year = json['Year'][:4]
            instance.save()
            messages.success(request, 'added recommendation', extra_tags='alert-success')
            return redirect(reverse("recommend"))
    recommended_today = Recommendation.objects.filter(date=timezone.now()).count()
    context = {
        'obj_list': Recommendation.objects.all().order_by('-date_insert'),
        'form': form,
        'count': {
            'today': recommended_today,
            'today2': recommended_today * 2
        },
    }
    return render(request, 'recommend/home.html', context)
