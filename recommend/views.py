from django.shortcuts import render, get_object_or_404, redirect

from .forms import RecommendForm
from .models import Recommendation

from prepareDB_utils import getOMDb


def recommend(request):
    form = RecommendForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        const = form.cleaned_data.get('const')
        json = getOMDb(const)
        instance.name = json['Title']
        instance.save()
    context = {
        'obj_list': Recommendation.objects.all().order_by('-date'),
        'form': form,
    }
    return render(request, 'recommend/home.html', context)