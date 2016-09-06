import datetime
now = datetime.datetime.now()
import calendar
import re

def strip_accents(s):
    """
    Usun znaki diakratyczne ze stringa
    http://stackoverflow.com/a/518232/5821316
    """
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def months_list():
    """
    Zwroc liste krotek (miesiac_po_polsku, miesiac_po_angielsku) bez polskich znakow
    http://stackoverflow.com/a/13037803/5821316
    """
    import locale
    # locale.setlocale(locale.LC_ALL, 'polish')
    # miesiace = [' ' + x for x in calendar.month_name[1:]]
    # miesiace = (strip_accents(' '.join(miesiace))).split(' ')
    # locale.setlocale(locale.LC_ALL, 'english')
    miesiace = (' styczen', ' luty', ' marzec', ' kwiecien', ' maj', ' czerwiec', ' lipiec', ' sierpien',
                ' wrzesien', ' pazdziernik', ' listopad', ' grudzien')
    months = [' ' + x.lower() for x in calendar.month_name[1:]]
    months_names = [(m.lower(), m2.lower()) for m, m2 in zip(miesiace, months)]
    return months_names


def check_for_month_name(napis):
    """
    Sprawdz czy zapytanie zawiera nazwe miesiaca po polsku/angielsku i zwroc jego numer
    """
    for i, (pol, ang) in enumerate(months_list(), 1):
        if pol[:4] in napis or ang[:4] in napis:
            return i

def matches_to_int(match):
    """
    Znalezione przez re.search cyfry zamienic ze stringa na int albo None
    """
    match_group_int = list()
    for match_group in match.groups():
        match_group_int.append(int(match_group) if match_group else None)
    return match_group_int

def get_date(dateformat="%d-%m-%Y", adddays=0):
    # import locale
    timenow = datetime.datetime.now()
    # locale.setlocale(locale.LC_ALL, 'polish')
    if adddays != 0:
        anothertime = timenow + datetime.timedelta(days=adddays)
    else:
        anothertime = timenow
    # locale.setlocale(locale.LC_ALL, 'english')
    return anothertime.strftime(dateformat)


def is_leap(varx):
    # if przestepny or czy
    match = re.search(r'(\d{4})[^0-9]*(\d{4})*', varx)        # todo {4}
    # kiedy najblizszy przestepny
    if 'nastep' in varx or 'kolej' in varx:
        for r in range(now.year + 1, 2050):         # todo bad
            if calendar.isleap(r):
                return 'nastepny rok przestepny jest w ' + str(r)
    elif not match:
        rok = now.year
    elif not match.group(2):
        rok = int(match.group(1))
    elif match.group(2):
        rok = int(match.group(1))
        rok2 = int(match.group(2))
        li = list()
        if rok > rok2:
            rok, rok2 = rok2, rok
        for y in range(rok, rok2 + 1):
            if calendar.isleap(y):
                li.append(y)
        li = ', '.join(map(str, li))
        return 'lata przestepne miedzy {}-{}: {} ({})'.format(rok, rok2, calendar.leapdays(rok, rok2 + 1), li)
    return str(rok) + ' jest przestepny' if calendar.isleap(rok) else 'nie jest przestepny'


def world_time(txt):
    import pytz
    from geopy import geocoders

    g = geocoders.GoogleV3()
    if txt:
        miasto = txt
        try:
            geocode = g.geocode(miasto)
        except:
            return 'mozliwy blad polaczenia z siecia'
        if geocode:
            place, (lat, lng) = g.geocode(miasto)
            timezone = g.timezone((lat, lng))
            local_time = datetime.datetime.now(pytz.timezone(timezone.zone))
            return {'lat': lat, 'lng': lng, 'place': place, 'time': local_time.strftime('%Y-%m-%d %A %H:%M:%S')}
    teraz = datetime.datetime.now()
    return teraz.strftime('aktualnie jest: %H:%M:%S')
