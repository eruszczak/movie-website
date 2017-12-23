from common.prepareDB_utils import get_csv_headers, valid_csv_header
from titles.constants import MY_HEADERS, MY_CSV_MAPPER, IMDB_HEADERS, IMDB_CSV_MAPPER


def recognize_file_source(f):
    headers = get_csv_headers(f)
    print(headers)
    if valid_csv_header(headers, MY_HEADERS):
        return MY_CSV_MAPPER
    elif valid_csv_header(headers, IMDB_HEADERS):
        return IMDB_CSV_MAPPER
    return None