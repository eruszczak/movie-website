from csv import DictReader, DictWriter
from io import StringIO

from django.utils.timezone import now
from os.path import join

from accounts.functions import validate_imported_ratings
from titles.helpers import fill_dictwriter_with_rating_qs
from common.prepareDB_utils import convert_to_datetime
from titles.models import Title, Rating


def import_ratings_from_csv(user, file):
    """
    from exported csv file import missing ratings. it doesn't add new titles, only new ratings
    file consists of lines in format: tt1234567,2017-05-23,7
    """
    file = file.read().decode('utf-8')
    io_string = StringIO(file)

    is_valid, message = validate_imported_ratings(file, io_string)
    if not is_valid:
        return 'error'

    return
    reader = DictReader(io_string)
    total_rows = 0
    created_count = 0
    for row in reader:
        total_rows += 1
        const, rate_date, rate = row['const'], row['rate_date'], row['rate']
        title = Title.objects.filter(const=const).first()
        rate_date = convert_to_datetime(row['rate_date'], 'exported_from_db')

        if title and rate_date:
            obj, created = Rating.objects.get_or_create(
                user=user, title=title, rate_date=rate_date, defaults={'rate': rate}
            )
            if created:
                created_count += 1

    return f'imported {created_count} out of {total_rows} ratings'


def export_ratings(user):
    """
    exports to a csv file all of user's ratings, so they can be imported later
    file consists of lines in format: tt1234567,2017-05-23,7
    """
    user_tmp_folder = user.get_temp_folder_path(absolute=True, create=True)
    headers = ['imdb_id', 'rate_date', 'rate']

    ratings = Rating.objects.filter(user=user).select_related('title')
    count_ratings = ratings.count()
    count_titles = ratings.values_list('title').distinct().count()

    filename = '{}_ratings_for_{}_titles_{}'.format(count_ratings, count_titles, now().strftime('%Y-%m-%d'))
    file_path = join(user_tmp_folder, f'{filename}.csv')
    with open(file_path, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=headers, lineterminator='\n')
        writer.writeheader()
        fill_dictwriter_with_rating_qs(writer, ratings)
    return file_path
