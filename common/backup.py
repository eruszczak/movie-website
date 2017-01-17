import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import json

from movie.models import Title


def backup():
    fields = Title._meta.get_fields()
    # my_field = Title._meta.get_field('my_field')
    print(fields)
    # related fields separately
    # posters manually copied
    fields = 'const name rate_imdb runtime year release_date votes url_poster url_imdb '
    fields += 'url_tomato tomato_meter tomato_rating tomato_reviews tomato_fresh tomato_rotten '
    fields += 'tomato_user_meter tomato_user_rating tomato_user_reviews tomatoConsensus plot'
    # x += 'plot img'
    # no slug and inserted/updated
    # cant have img
    complex_attrs = 'genre actor director type img'
    data = {}
    for title in Title.objects.all():
        attrs = {}
        for field in fields.split():
            attrs[field] = getattr(title, field)
        data[getattr(title, 'const')] = str(attrs)

        for field in complex_attrs.split():
            if field == 'img' and getattr(title, field):
                data['img'] = getattr(title, field).url
            elif field == 'type':
                pass
                # one to many
                # just check related field name
            else:
                pass
                # director genre
                # model._meta.many_to_many   all related field names

    print(data)
    with open('backup.json', 'w') as f:
        json.dump(data, f)


backup()