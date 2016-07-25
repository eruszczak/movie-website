from django.shortcuts import render
import pygal
from movie.models import Genre, Entry
from django.db.models import Count


def chart_genres():
    line_chart = pygal.Bar()
    line_chart.title = 'Rated genres distribution'
    genres = Genre.objects.all().annotate(num=Count('entry')).order_by('-num')
    for g in genres:
        line_chart.add({
            'title': '{1} {0}'.format(g.name, g.entry_set.count()),
            'xlink': {
                'href': g.get_absolute_url(),
                'target': '_blank',
            }
        }, [{
            'value': g.entry_set.count(),
            'xlink': {
                'href': g.get_absolute_url(),
                'target': '_blank',
            }
        }])
    return line_chart.render()


def chart_ratings():
    line_chart = pygal.Bar()
    line_chart.title = 'Rating distribution'
    rate_count = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
    rate_count = sorted(rate_count, key=lambda x: int(x['rate']))
    # line_chart.x_labels = [x['rate'] for x in rate_count]

    for obj in rate_count:
        line_chart.add(obj['rate'], obj['the_count'])

    return line_chart.render()


def home(request):
    chart_g = chart_genres()
    chart_r = chart_ratings()

    return render(request, 'chart/index.html', {'chart': chart_g, 'chart_ratings': chart_r})