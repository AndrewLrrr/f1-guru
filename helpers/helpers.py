from datetime import datetime, timedelta
import re


def add_milliseconds_to_time(time, ms):
    t = datetime.strptime(time, '%M.%S.%f')
    t = t + timedelta(milliseconds=ms)
    t = datetime.strftime(t, '%M.%S.%f')
    return re.sub('^0*([\d.]+?)0*$', r'\1', t)
