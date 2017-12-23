import csv
from datetime import datetime
from xml.etree import ElementTree

import requests

from titles.constants import MY_HEADERS, MY_CSV_MAPPER, IMDB_HEADERS, IMDB_CSV_MAPPER


def recognize_file_source(f):
    headers = get_csv_headers(f)
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
    return csv_headings


def valid_csv_header(headers, expected_headers):
    """return True if all of expected headers are present in headers"""
    return all(h in headers for h in expected_headers)


def fill_dictwriter_with_rating_qs(writer, ratings):
    for r in ratings:
        writer.writerow({
            'imdb_id': r.title.imdb_id,
            'rate_date': r.rate_date,
            'rate': r.rate
        })


def get_imdb_rss(url):
    """gets XML from rss.imdb.com/user/<userid>/{ratings} or {watchlist}"""
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return ElementTree.fromstring(response.text).findall('channel/item')
    return None


def unpack_from_rss_item(obj, for_watchlist=False):
    """
    parses <item> from rss.imdb.com/user/<userid>/ratings or watchlist
    * if rating item: get title's const, rating date and rating
    * if watchlist item: get title's const and added date
    """
    const = obj.find('link').text[-10:-1]
    date = convert_to_datetime(obj.find('pubDate').text, 'xml')
    if for_watchlist:
        # todo
        # date += timedelta(hours=7)
        # date = date.replace(tzinfo=pytz.timezone('UTC'))
        return const, date

    rate = obj.find('description').text.strip()[-3:-1].lstrip()
    return const, date, rate
