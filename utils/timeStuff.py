import re

import arrow
import datetime
from dateutil.relativedelta import relativedelta


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


def human_join(seq, delim=', ', final='or'):
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'


def convertTimeToReadable1(time):
    dd = arrow.get(time).datetime
    epoch = (dd.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()
    return str(datetime.datetime.utcfromtimestamp(int(epoch)).strftime('%d/%m/%Y %H:%M:%S'))


# credit to Danny
def human_timedelta(dt, *, source=None, accuracy=3, brief=False, suffix=True):
    now = source or datetime.datetime.utcnow()
    # Microsecond free zone
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    # This implementation uses relativedelta instead of the much more obvious
    # divmod approach with seconds because the seconds approach is not entirely
    # accurate once you go over 1 week in terms of accuracy since you have to
    # hardcode a month as 30 or 31 days.
    # A query like "11 months" can be interpreted as "!1 months and 6 days"
    if dt > now:
        delta = relativedelta(dt, now)
        suffix = ''
    else:
        delta = relativedelta(now, dt)
        suffix = ' ago' if suffix else ''

    attrs = [
        ('year', 'y'),
        ('month', 'mo'),
        ('day', 'd'),
        ('hour', 'h'),
        ('minute', 'm'),
        ('second', 's'),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + 's')
        if not elem:
            continue

        if attr == 'day':
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), 'week'))
                else:
                    output.append(f'{weeks}w')

        if elem <= 0:
            continue

        if brief:
            output.append(f'{elem}{brief_attr}')
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return 'now'
    else:
        if not brief:
            return human_join(output, final='and') + suffix
        else:
            return ' '.join(output) + suffix


def convert_sec_to_smh(sec):
    if sec < 60:
        tim = f'{int(sec)}s'
    elif 3600 > sec >= 60:
        tim = f'{int(sec // 60)}m'
    else:
        tim = f'{int(sec // 3600)}h {int((sec // 60) % 60)}m'
    return tim


def get_time_from_str_and_possible_err(string):
    try:
        error = ""
        date = None
        ds = tuple(map(int, re.findall(r'\d+', string)))[:6]
        if ds:
            date = datetime.datetime(*ds)
        else:
            error = "Couldn't find any numbers while parsing date."
    except Exception as e:
        date = None
        ee = str(e).replace('@', '@\u200b')
        error = (f"Something went wrong when parsing time. "
                 f"Please check your "
                 f"syntax and semantics. Exception:\n"
                 f"```\n{ee}```")

    return date, error
