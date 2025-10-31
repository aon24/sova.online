'''
Created on 17 мая 2025 г.

@author: aon24
'''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arm.settings')
django.setup()

from arm.tools.DC import DC, toWell, getBody, config
from nv.models import SessionGr

from datetime import datetime
from dateutil.relativedelta import relativedelta


# *** *** ***
def shiftM(dateStr):
    if dateStr:
        try:
            date = datetime.strptime(dateStr, "%Y-%m-%d")
            new_date = date + relativedelta(months=1)  # Добавляем 1 месяц
            return new_date.strftime("%Y-%m-%d")
        except:
            pass
    return ''


LAST_UPDATE = ''


def main(m):
    '''
    Только для демо!!!
    стартует раз в месяц и сдвигает расписание на 1 месяц
    запоминает в сессиях групп дату(гггг-мм) последнего обновления
    '''
    # if not config.demo_mode:
    #     raise Exception('AAAAAAAAAA')

    i = j = 0
    for p in SessionGr.objects.values().all():
        dc = getBody(p)

        if LAST_UPDATE:
            if dc.lastUpdate != LAST_UPDATE:
                dc.lastUpdate = LAST_UPDATE
                dcUK = DC(dbAlias='nv_SessionGr', unid=dc.id, _superUser=1)
                dcUK.doc = dc
                dcUK.save()
            continue

        y_m = datetime.today().strftime('%Y-%m')
        if not dc.lastUpdate or dc.lastUpdate < y_m:
            dc.lastUpdate = y_m

            dc.date_begin_old = dc.date_begin_old or dc.date_begin  # на всякий случай
            dc.date_end_old = dc.date_end_old or dc.date_end  # на всякий случай

            dc.date_begin = shiftM(dc.date_begin)
            dc.date_end = shiftM(dc.date_end)

            dcUK = DC(dbAlias='nv_SessionGr', unid=dc.id, _superUser=1)
            dcUK.doc = dc
            dcUK.save()
            j += 1
        i += 1
    m.log = f'SessionGr: {i}. Changed: {j}'

# *** *** ***


if __name__ == '__main__':
    from arm.tools.loadWell import loadWell
    m = DC()

    toWell(1, 'busy')
    main(m)
    toWell(0, 'busy')

    loadWell('all')
    print(m)
