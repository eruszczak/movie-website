from csv import DictReader
from io import StringIO

from accounts.functions import validate_imported_ratings
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


