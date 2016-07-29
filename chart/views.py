from django.shortcuts import render
from .forms import ChartForm
from .charts import *


def home(request):
    chart = ''
    if request.method == 'POST':
        form = ChartForm(request.POST)
        if form.is_valid():
            chart = form.cleaned_data['chart']
            if chart == 'chart_genres':
                chart = chart_genres()
            if chart == 'chart_ratings':
                chart = chart_ratings()
            if chart == 'chart_last_year_ratings':
                chart = chart_last_year_ratings()
            if chart == 'distribution_by_year':
                chart = distribution_by_year()
    else:
        form = ChartForm
    # chart_g = chart_genres()
    # chart_r = chart_ratings()
    # chart_l = chart_last_year_ratings()
    # chart_sparks = distribution_by_year()
    context = {
        'form': form,
        'chart': chart,
        # 'chart_genres': chart_g,
        # 'chart_ratings': chart_r,
        # 'chart_last_year_ratings': chart_l,
        # 'chart_sparks': chart_sparks,
    }
    return render(request, 'chart/index.html', context)
