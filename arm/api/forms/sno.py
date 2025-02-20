# -*- coding: utf-8 -*-
'''
Created 2021

@author: aon

'''

from arm.tools.dbToolkit.Book import setDocNo
from arm.tools.first import snd, err

# *** *** ***


def snoDB(dcUK):
    dbAlias = dcUK.dbAlias
    n = setDocNo(dbAlias) or ''
    if n:
        snd(f'{dcUK.fullName}: зарегистрирован номер {n} в {dbAlias}', cat='Регистрация')
    else:
        err(f'{dcUK.fullName}: номер не сохранен в {dbAlias} из-за ошибки', cat='Регистрация')
    return n

# *** *** ***
