import re
import calendar
import datetime
from . import funkcje as f
now = datetime.datetime.now()


def ile_dni(query):
    match = re.search(r'[^0-9]*(\d*)[^0-9]*', query)
    mies = now.month
    if match.group(1) and not f.check_for_month_name(query):
        if 0 < int(match.group(1)) <= 12:
            mies = int(match.group(1))
    elif f.check_for_month_name(query):
        mies = f.check_for_month_name(query)
    return '{} {} ma {} dni'.format(f.months_list()[mies - 1][0], now.year, calendar.monthrange(now.year, mies)[1])


def kalendarz(var):
    rok, miesiac = now.year, now.month
    s = ''
    if 'rok' in var or 'rocz' in var:
        s = calendar.calendar(rok)
        return
    if f.check_for_month_name(var):
        miesiac = f.check_for_month_name(var)
        s += calendar.month(rok, miesiac)
        return
    s += calendar.month(rok, miesiac)
    return s

def jaka_godzina():
    teraz = datetime.datetime.now()
    return teraz.strftime('%H:%M:%S')


def jaki_dzien(var):
    day = 0
    szukaj_dnia = re.search(r'([\d]+)', var)

    if szukaj_dnia:
        day = int(szukaj_dnia.group(1))
        if 'temu' in var or 'ago' in var:
            day = -day
    else:
        skroty = [('przedwczor', 'before yes', -2), ('wczor', 'yester', -1), ('dzis', 'toda', 0),
                  ('jutro', 'tommo', 1), ('pojutrz', 'after tom', 2), ('tydzie', 'week', 7)]
        for (pol, ang, v) in skroty:
            if pol in var or ang in var:
                day = v
                break

    d_format = '%Y-%m-%d %A'
    if 'dzien tyg' in var:
        d_format = '%A'
    new_date = f.get_date(d_format, day)
    return new_date.title()


def kiedy(napis):
    rok, miesiac, dzien = now.year, 1, 1
    month_number = f.check_for_month_name(napis) if f.check_for_month_name(napis) else False
    match = re.search(r'[^0-9]*(\d\d\d\d)*[^0-9]*(\d\d?)*[^0-9]*(\d\d?)*', napis)
    found_year, found_month, found_day = f.matches_to_int(match)
    if all(x is None for x in match.groups()) and not month_number:
        return 'kiedy'  # jesli nie podano zadnych liczb/nazwy miesiaca
    if found_year:
        rok = found_year
        if found_month and not month_number:  # jesli znaleziono numer, ale nie znaleziono nazwy
            miesiac = found_month
            if found_day:
                dzien = found_day
            else:
                if month_number:
                    miesiac = month_number
                    dzien = found_month  # jesli podano pelna date, ale zamiast nr miesiaca jego nazwe
        else:
            if month_number:  # jesli znaleziono nazwe miesiaca
                miesiac = month_number
                if found_month:  # jesli nazwa miesiaca i numer miesiaca (wtedy numer staje sie dniem, tak j/w)
                    dzien = found_month
    elif found_month:  # nie znaleziono roku
        miesiac = found_month
        if month_number:
            miesiac = month_number
            if found_day:
                dzien = found_day
        if found_day:
            dzien = found_day
        if month_number and not found_day:
            dzien = found_month
    # elif found_day:  # znaleziono
    #     dzien = found_day
    else:
        miesiac = month_number  # jesli nie podano zadnych liczb, sprawdz czy chociaz podano nazwe miesiaca

    if not 1 <= miesiac <= 12 or not 1 <= dzien <= calendar.monthrange(rok, miesiac)[1]:
            print('error day/month')
            return

    if 'ost' in napis and not found_day:
        dzien = calendar.monthrange(rok, miesiac)[1]
        if not found_month and not month_number:
            miesiac = 12

    delta = datetime.date(rok, miesiac, dzien) - datetime.date(now.year, now.month, now.day)
    czas = delta.days

    output = ''
    if 'godz' in napis or 'hour' in napis:
        czas *= 24
        output += str(abs(czas)) + ' godzin'
    elif 'min' in napis:
        czas *= 24 * 60
        output += str(abs(czas)) + ' minut'

    s = '{}-{}-{} '.format(rok, miesiac, dzien)
    if delta.days >= 0:
        s += 'za ' + output if output else 'za ' + str(delta.days) + ' dni'
    else:
        s += output + ' temu' if output else str(abs(delta.days)) + ' dni temu'
    return s

def get_answer(text=None):
    # while True:
    #     text = input('>> ')
    text = f.strip_accents(text).lower()
    if any(x in text for x in ['kiedy', 'when', 'za ile']) and 'przestep' not in text:
        return kiedy(text)
    elif 'przeste' in text or 'leap' in text:
        return f.is_leap(text)
    elif any(x in text for x in ['jaki', 'what', 'co']) and not any(x in text for x in ['czas', 'teraz']):
        return jaki_dzien(text.replace(' dzien', ''))
    elif any(x in text for x in ['czas', 'godzina', 'teraz']):
        return jaka_godzina()
    elif 'ile' in text:
        return ile_dni(text)
    elif 'kalen' in text or 'calend' in text:
        return kalendarz(text)
    elif 'time' in text:
        return f.world_time(text.replace('time', ''))
    # if text in ('koniec', 'end', '0', 'stop'):
    #     print('koniec programu')
    #     break

# if __name__ == '__main__':
#     get_answer()
