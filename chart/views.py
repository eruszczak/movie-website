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
    from django.core.urlresolvers import reverse
    line_chart = pygal.Bar()
    line_chart.title = 'Rating distribution'
    rate_count = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
    rate_count = sorted(rate_count, key=lambda x: int(x['rate']), reverse=True)
    # line_chart.x_labels = [x['rate'] for x in rate_count]

    for obj in rate_count:
        # line_chart.add('{} ({})'.format(obj['rate'], obj['the_count']), obj['the_count'])
        link = reverse('entry_show_from_rate', kwargs={'rate': obj['rate']})
        line_chart.add({
            'title': '{} ({})'.format(obj['rate'], obj['the_count']),
            'xlink': {
                'href': link,
                'target': '_blank',
            }
        }, [{
            'value': obj['the_count'],
            'xlink': {
                'href': link,
                'target': '_blank',
            }
        }])
    return line_chart.render()


def chart_last_year_ratings():
    line_chart = pygal.Bar()
    line_chart.title = 'Browser usage evolution (in %)'
    # line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.x_labels = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
    return line_chart.render()

def home(request):
    chart_g = chart_genres()
    chart_r = chart_ratings()
    chart_l = chart_last_year_ratings()

    context = {
        'chart_genres': chart_g,
        'chart_ratings': chart_r,
        'chart_last_year_ratings': chart_l,
    }
    return render(request, 'chart/index.html', context)