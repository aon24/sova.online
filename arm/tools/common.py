# -*- coding: utf-8 -*-
"""
AON 2020
"""

from arm.tools.first import err

import re, os
from datetime import datetime
import traceback


# *** *** ***

busyFunc = {}

# *** *** ***



def checkBusy(func):
    """
    Декоратор, блокирующий повторный вызов функции.
    """

    def _wrapper(*args, **kwargs):
        if not busyFunc.get(func.__name__):
            try:
                busyFunc[func.__name__] = True
                func(*args, **kwargs)
            except Exception as ex:
                err(f'{func.__name__}: {ex}', cat='amgrRun.checkBusy')
            finally:
                busyFunc[func.__name__] = False

    return _wrapper

# *** *** ***

def cleanPhone(phone):
    phone = re.sub(r'[^\d]', '', phone or '')
    if phone:
        return '+7' + phone[1:] if phone[0] == '8' else '+' + phone
    return ''


# *** *** ***


def now(dlm='.'):
    if dlm == '.':
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    elif dlm == '_':
        return datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    else:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# *** *** ***


def today(dlm='.'):
    if dlm == '.':
        return datetime.today().strftime('%d.%m.%Y')
    else:
        return datetime.today().strftime('%Y-%m-%d')

# *** *** ***

js_search = re.compile(r'((<script[\s]+src[\s]*)|(<link[\s]+rel[\s]*))=[\s]*[\'"][\s\S]+?(\.css"|\.js"|\.json")', re.IGNORECASE | re.M | re.U)

def setVersionJS(bf, path):
    """
bf =
...
<script src="/api/jsv?lb.js"></script>
<link rel="stylesheet" href="jsv?std3d.css"/>

returned:
...
[
<script src="/api/jsv?lb.js::2013-09-02 09:57:24"></script>
<link rel="stylesheet" href="/api/jsv?std3d.css::2013-08-29 13:16:28"/>
, ver
]
    """
    itr = js_search.finditer(bf)
    l0 = 0
    bf2 = ''
    ver = ''
    for match in itr:
        s = match.group()
        if 'jsv?' in s:
            s = s[:-1]
            fn = os.path.join(path, s.partition('jsv?')[2])
            try:
                stat = os.stat(fn)
                v = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y-%H:%M:%S')
                s += '::' + v
                ver = max(ver, v)
            except Exception as ex:
                s = s.replace('jsv?', 'js?')
                err(f'\nfn:"{fn}" not found\n{ex}', cat='setVersionJS')

        s += '"'

        l1, l2 = match.span()
        bf2 += bf[l0:l1] + s
        l0 = l2

    return bf2 + bf[l0:], ver

# *** *** ***


def setVersionFiles(ls, path):
    ols = []
    if ls:
        if type(ls) is str:
            ls = [ls]
        for s in ls:
            if 'jsv?' not in s:
                s and ols.append(s)
            else:
                fn = os.path.join(path, s.partition('jsv?')[2])
                try:
                    stat = os.stat(fn)
                    v = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y-%H:%M:%S')
                    ols.append(s + '::' + v)
                except:
                    err(f'"{fn}" not found', cat='setVersionFiles')
    return ols

# *** *** ***


def sndErr(func):
    """
    Декоратор. Вызывает функцию func и ловит Exception.
    Если поймал:
        - выводит имя функции и сообщение об ошибке
        - возвращает None.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            err(f'{ex}\n{traceback.format_exc()}', cat=f'Y-{func.__name__}')

    return wrapper

# *** *** ***

