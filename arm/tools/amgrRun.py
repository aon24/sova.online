'''
Created on 2024

@author: aon24
'''
from arm.tools.common import now, checkBusy
from arm.tools.first import snd, err
from arm.tools.DC import DC
from arm.tools.dbToolkit.Book import snoDB
from nv_lm.models import Module

import importlib
import traceback
import json

# *** *** ***


@checkBusy  # Декоратор, блокирующий повторный вызов функции до ее завершения.
def runAgent(m):
    m.starting_time = now('-')
    Module.objects.filter(id=m.id).update(starting_time=m.starting_time)
    try:
        m.log = ''

        cat = 'Agent manager'
        path = f'nv_lm.agents.{m.module}'

        snd(f'Start: {path}("{m.param}"). {m.title}', cat=cat)

        mmm = importlib.import_module(path)
        mmm = importlib.reload(mmm)
        htmlList = mmm.main(m)  # может что-то записать в поле 'log'

        if htmlList:  # если агент возвращает список, создается гл.док(отчет с номером) и подчиненные(refs) из списка
            report = DC(dbAlias='nv_lm_Module', fullName='runAgent')
            report.doc = DC(
                form='Report',
                title=m.title,
                status='active',
                docNo=snoDB(report),
                starting_time=m.starting_time,
                end_time=now('-'),
                log=m.log,
            )

            reportId = report.save().id

            for html in htmlList:
                ref = DC(dbAlias='nv_lm_Module', fullName=cat)
                ref.doc = DC(ref=reportId, form='html', status='active')
                ref.doc.html = json.dumps(html.get('body', ''), ensure_ascii=False)
                ref.doc.title = html.get('title', '')
                ref.save()

        m.end_time = now('-')
        m._run = ''
        if m.SCHEDULED == 'now':
            m.TURN_ON = ''  # 1 раз и нефиг
        dc = DC(dbAlias='nv_lm_Module', unid=m.id, fullName=cat)
        dc.doc = m
        dc.save()
        snd(f'End: {m.title}', cat=cat)

    except Exception as ex:
        m.turn_on = m._run = ''
        s = f'{m.title}\n{ex}\n{traceback.format_exc()}'
        m.log += s
        err(s, cat=cat)
        dc = DC(dbAlias='nv_lm_Module', unid=m.id, fullName=cat)
        dc.doc = m
        dc.save()

# *** *** ***
