from django.shortcuts import render
import pygal
from movie.models import Genre, Entry
from django.db.models import Count
from django.core.urlresolvers import reverse


def chart_genres():
    line_chart = pygal.Bar()
    line_chart.title = 'Rated genres distribution'
    genres = Genre.objects.all().annotate(num=Count('entry')).order_by('-num')
    for g in genres:
        line_chart.add({
            'title': '{1} {0}'.format(g.name, g.entry_set.count()),
            'xlink': {
                'href': g.get_absolute_url(),
                # 'target': '_blank',
            }
        }, [{
            'value': g.entry_set.count(),
            'xlink': {
                'href': g.get_absolute_url(),
                # 'target': '_blank',
            }
        }])
    return line_chart.render()


def chart_ratings():
    line_chart = pygal.Bar()
    line_chart.title = 'Rating distribution'
    rate_count = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
    rate_count = sorted(rate_count, key=lambda x: int(x['rate']), reverse=True)
    # line_chart.x_labels = [x['rate'] for x in rate_count]

    for obj in rate_count:
        link = reverse('entry_show_from_rate', kwargs={'rate': obj['rate']})
        line_chart.add({
            'title': '{} ({})'.format(obj['rate'], obj['the_count']),
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }, [{
            'value': obj['the_count'],
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }])
    return line_chart.render()


def count_for_month_lists(year):
    from django.db import connection
    query = """SELECT COUNT(*) AS 'the_count', strftime("%%m", rate_date) as 'month'
    FROM movie_entry
    WHERE strftime("%%Y", rate_date) = %s
    GROUP BY month"""
    cursor = connection.cursor()
    cursor.execute(query, [str(year)])
    return list(cursor.fetchall())


def chart_last_year_ratings(year=2015):
    from datetime import datetime
    import calendar
    year = datetime.now().year - 1
    line_chart = pygal.Bar()
    line_chart.title = 'Total count of watched titles for each month in {}'.format(year)
    get_data = count_for_month_lists(year)

    for count, month in get_data:
        link = reverse('entry_show_rated_in_month', kwargs={'year': year, 'month': month})
        line_chart.add({
            'title': '{} {}'.format(count, calendar.month_name[int(month)]),
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }, [{
            'value': count,
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }])
    return line_chart.render()


def sparklines_for_years():
    data = Entry.objects.values('year').annotate(the_count=Count('year')).order_by('year')
    line_chart = pygal.Bar(show_legend=False)
    line_chart.title = 'Rating distribution by year'
    for obj in data:
        link = reverse('entry_show_from_year', kwargs={'year': obj['year']})
        line_chart.add({
            'title': '{} ({})'.format(obj['year'], obj['the_count']),
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }, [{
            'value': obj['the_count'],
            'xlink': {
                'href': link,
                # 'target': '_blank',
            }
        }])
    return line_chart.render()


def home(request):
    chart_g = chart_genres()
    chart_r = chart_ratings()
    chart_l = chart_last_year_ratings()
    chart_sparks = sparklines_for_years()

    context = {
        'chart_genres': chart_g,
        'chart_ratings': chart_r,
        'chart_last_year_ratings': chart_l,
        'chart_sparks': chart_sparks,
    }
    return render(request, 'chart/index.html', context)
