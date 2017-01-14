import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import json

from movie.models import Title


def backup():
    # related fields separately
    # posters manually copied
    x = 'const name rate_imdb runtime year release_date votes url_poster url_imdb '
    x += 'url_tomato tomato_meter tomato_rating tomato_reviews tomato_fresh tomato_rotten '
    x += 'tomato_user_meter tomato_user_rating tomato_user_reviews tomatoConsensus plot'
    # x += 'plot img'
    # no slug and inserted/updated
    # cant have img
    complex_attrs = 'genre actor director type img'
    data = {}
    for title in Title.objects.all():
        attrs = {}
        for field in x.split():
            attrs[field] = getattr(title, field)
        data[getattr(title, 'const')] = str(attrs)

        for field in complex_attrs.split():
            if field == 'img':
                pass
                # img.url  attrs[field] = getattr(title, field).url
            elif field == 'type':
                pass
                # one to many
                # just check related field name
            else:
                pass
                # many to many
                # model._meta.many_to_many   all related field names

    print(data)
    with open('backup.json', 'w') as f:
        json.dump(data, f)


backup()