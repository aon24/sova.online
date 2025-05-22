# -*- coding: utf-8 -*-
'''
Created on 2024

@author: aon24
'''
from arm.tools.first import err
from arm.tools.common import today, now, busyFunc
from arm.tools.DC import well, toWell
from arm.tools.loadWell import loadWell
from arm.tools.amgrRun import runAgent
from arm.tools.makeReport import startReport

import threading
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

# *** *** ***

def amgrLoop():
    '''
    m._run нигде не проверяется. Нужна для отображения в виде синем цветом
    '''

    while True:
        if well('reloadWell') and not well('busy'):
            toWell(0, 'reloadWell')
            loadWell('all')
        if not busyFunc.get('runAgent'):
            m = checkSchedule('turnOnList')
            if m:
                try:
                    m._run = 1
                    threading.Thread(target=runAgent, args=[m]).start()
                except Exception as ex:
                    err(ex, cat='amgr.runAgent')
                    m.turn_on = m._run = ''

        if not busyFunc.get('startReport'):
            m = checkSchedule('turnOnReport')
            if m:
                try:
                    m._run = 1
                    threading.Thread(target=startReport, args=[m]).start()
                except Exception as ex:
                    err(ex, cat='amgr.startReport')
                    m.turn_on = m._run = ''
        time.sleep(1)

# *** *** ***


def checkSchedule(turnOnList):
    ls = well(turnOnList)
    forDel = []
    for d in ls:
        if not d.turn_on:
            forDel.append(d)
            continue

        if d.scheduled == 'now':
            if d.starting_time:
                forDel.append(d)
                continue
            return d

        if d.runByStart and not d.starting_time:
            return d

        if d.schedTime:
            try:
                if d.scheduled == 'interval':
                    tm = time.mktime(time.strptime(d.end_time or d._modified or d._created, '%Y-%m-%d %H:%M:%S'))
                    if time.time() - tm > int(d.schedTime) * 60:
                        return d

                elif d.end_time.partition(' ')[0] != today('-') and checkTime(d):  # не запускался(закончился) сегодня
                    return d
            except Exception as ex:
                err(ex, cat='amgr.heckSchedule')
                d.end_time = d._modified = now('-')
                d.turn_on = ''
                forDel.append(d)

    for d in forDel:
        ls.remove(d)

# *** *** ***


def checkTime(d):
    dt = datetime.now()
    year, month, day, hour, minutes, sec, weekday, yday, isdst = dt.timetuple()

    hh = int(d.schedTime.split(':')[0])
    mm = int(d.schedTime.split(':')[1])

    if hour > hh or (hour == hh and minutes >= mm):
        if d.scheduled == 'daily':
            return True

        schedDay = int(d.schedDay)
        if d.scheduled == 'weekly':
            return weekday == schedDay

        if d.scheduled == 'monthly':
            if schedDay < 0:
                dt += relativedelta(day=31)
                schedDay += dt.day + 1
            return day == schedDay

