from pytz import timezone, utc
from datetime import datetime
import os

def customtime():
    utc_dt = datetime.now(utc)
    my_tz = timezone(os.environ['TIMEZONE'])
    converted = utc_dt.astimezone(my_tz)
    date = converted.strftime("%m/%d/%Y %H:%M:%S")
    return date