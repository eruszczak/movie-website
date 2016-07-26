from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .forms import RecommendForm
from .models import Recommendation

from prepareDB_utils import getOMDb
from django.contrib import messages


def recommend(request):
    form = RecommendForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        const = form.cleaned_data.get('const')
        json = getOMDb(const)
        if json:
            instance.name = json['Title']
        instance.save()
        messages.success(request, 'added recommendation', extra_tags='alert-success')
        return redirect(reverse("recommend"))
    context = {
        'obj_list': Recommendation.objects.all().order_by('-date_insert'),
        'form': form,
    }
    return render(request, 'recommend/home.html', context)