from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .forms import RecommendForm
from .models import Recommendation

from prepareDB_utils import getOMDb
from django.contrib import messages
from django.utils import timezone


def recommend(request):
    form = RecommendForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        const = form.cleaned_data.get('const')
        json = getOMDb(const)
        if json:
            instance.name = json['Title']
            instance.year = json['Year']
        instance.save()
        messages.success(request, 'added recommendation', extra_tags='alert-success')
        return redirect(reverse("recommend"))
    context = {
        'obj_list': Recommendation.objects.all().order_by('-date_insert'),
        'form': form,
        'todays_count': Recommendation.objects.filter(date=timezone.now()).count() * 2
    }
    return render(request, 'recommend/home.html', context)