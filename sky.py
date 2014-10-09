import ephem
from pytz import utc, timezone

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

def sunset(observer, date):
    observer.date = date.astimezone(utc)
    return observer.next_setting(sun).datetime().replace(tzinfo=utc)

def moonset(observer, date):
    observer.date = date.astimezone(utc)
    return observer.next_setting(moon).datetime().replace(tzinfo=utc)

