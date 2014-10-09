import ephem
from pytz import utc, timezone
from datetime import timedelta
from copy import copy


sun = ephem.Sun()
moon = ephem.Moon()
est = timezone('EST')

def get_observer():
    location = ephem.Observer()
    location.lon = '-83:23:24'
    location.lat = '40:13:48'
    location.elevation = 302
    location.pressure = 0
    location.horizon = '-0:34'
    return location

    
def sunrise(observer, date):
    observer.date = date.astimezone(utc)
    return observer.next_rising(sun).datetime().replace(tzinfo=utc)

def sunrises(observer, start_date, offset_seconds=0):
    # offset negative before, positive after
    current_date = copy(start_date)
    while 1:
        yield sunrise(observer, current_date) + timedelta(seconds=offset_seconds)
        current_date = current_date + timedelta(days=1)


def sunset(observer, date):
    observer.date = date.astimezone(utc)
    return observer.next_setting(sun).datetime().replace(tzinfo=utc)

def sunsets(observer, start_date, offset_seconds=0):
    # offset negative before, positive after
    current_date = copy(start_date)
    while 1:
        yield sunset(observer, current_date) + timedelta(seconds=offset_seconds)
        current_date = current_date + timedelta(days=1)


def moonset(observer, date):
    observer.date = date.astimezone(utc)
    return observer.next_setting(moon).datetime().replace(tzinfo=utc)

def moonsets(observer, start_date, offset_seconds=0):
    # offset negative before, positive after
    current_date = copy(start_date)
    while 1:
        yield moonset(observer, current_date) + timedelta(seconds=offset_seconds)
        current_date = current_date + timedelta(days=1)

