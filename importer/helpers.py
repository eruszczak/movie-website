import csv
from datetime import datetime

from titles.constants import MY_HEADERS, MY_CSV_MAPPER, IMDB_HEADERS, IMDB_CSV_MAPPER


def recognize_file_source(f):
    headers = get_csv_headers(f)
    print(headers)
    if valid_csv_header(headers, MY_HEADERS):
        return MY_CSV_MAPPER
    elif valid_csv_header(headers, IMDB_HEADERS):
        return IMDB_CSV_MAPPER
    return None


def convert_to_datetime(date_string, source):
    """
    xml is IMDb's RSS format (for getting current ratings and watchlist)
    csv is for ratings.csv file exported from IMDb list
    json is OMDb's API format
    exported_from_db is my format, used when ratings are exported or imported (user profile)
    """
    date_formats = {
        'imdb_xml': '%a, %d %b %Y %H:%M:%S GMT',
        'csv': '%Y-%m-%d'
    }
    if date_formats.get(source):
        try:
            return datetime.strptime(date_string, date_formats[source])
        except ValueError:
            pass
    return None


def get_csv_headers(file):
    """
    get first line from opened csv file or iostring and return list of its csv headers
    must call seek method to restore current position to beginning of the file
    """
    csv_reader = csv.reader(file)
    csv_headings = next(csv_reader)
    file.seek(0)
    # if len(csv_headings) == 1:
    #     # imdb csv file uses only 1 column so all headers are in 1 column
    #     print('before', csv_headings)
    #     csv_headings = csv_headings[0].replace('"', '').split(',')
    #     print('after', csv_headings)
    return csv_headings


def valid_csv_header(headers, expected_headers):
    """return True if all of expected headers are present in headers"""
    print([h in headers for h in expected_headers])
    return all(h in headers for h in expected_headers)