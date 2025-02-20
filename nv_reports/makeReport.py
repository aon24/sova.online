'''
Created on 2024

@author: aon24
'''
from arm.tools.common import now, checkBusy
from arm.tools.DC import DC
from arm.tools.first import snd, err
from arm.api.forms.sno import snoDB
from arm.tools.dbToolkit.DJ import docFromDB

from nv_reports.models import Report

import importlib
import traceback
import json

# *** *** ***

def makeReport(agent):
    '''
    создает в базе отчетов заготовку отчета
    вызывается из amgr по расписанию(agent - dc object-Module, form=lm)
    или из v_reports, если выбрано "сейчас 1 раз"(agent - dc-obj from v_reports)
    заготовка аналогична агенту с расписанием "выполнить сейчас 1 раз"
    agent - dc object, form=lm
    '''
    report = DC(dbAlias='nv_reports_Report', fullName='makeReport')
    report.doc = DC(form='report')
    for k in agent.keys():
        l, _, r = k.partition('_')
        if l == 'REPORT':
            report.doc[r] = agent[k]

    report.doc.title = agent.title
    report.doc.scheduled = 'now'
    report.doc.turn_on = 1
    report.doc.status = 'active'
    report.doc.lmRef = agent.id
    report.doc.docNo = snoDB(report)

    if report.save():
        snd(agent.report_title, cat='Report created')

# *** *** ***


@checkBusy  # Декоратор, блокирующий повторный вызов функции до ее завершения.
def startReport(report):
    """
    вызывается из amgr
    """
    cat = 'Report run'
    path = f'nv_reports.{report.domain}.{report.module}'
    snd(f'Start: {path}\n{report.title}', cat=cat)

    report.starting_time = now('-')
    Report.objects.filter(pk=report.pk).update(starting_time=report.starting_time)

    try:
        mmm = importlib.import_module(path)
        importlib.reload(mmm)
        htmlList = mmm.main(report) or []

        report.end_time = now('-')
        report.turn_on = report._run = ''
        dc = DC(dbAlias='nv_reports_Report', unid=report.pk, fullName=cat)
        docFromDB(dc)
        dc.doc = report
        dc.save()

        for html in htmlList:
            ref = DC(dbAlias='nv_reports_Report', fullName=cat)
            ref.doc = DC(ref=report.id, form='html', status='active')
            ref.doc.html = json.dumps(html.main, ensure_ascii=False)
            for k in ['title', 'reportName', 'addList']:
                ref.doc[k] = html[k] or report[k]

            ref.save()

        snd(f'Finish: {report.title}', cat=cat)

    except Exception as ex:
        report.turn_on = report._run = ''
        s = f'{report.title}\n{ex}\n{traceback.format_exc()}'
        report._log += s
        err(report, cat=cat)
        dc = DC(dbAlias='nv_reports_Report', unid=report.id, fullName=cat)
        docFromDB(dc)
        dc.doc = report
        dc.save()

        if report.lmRef:
            dc = DC(dbAlias='nv_lm_Module', unid=report.lmRef, fullName=cat)
            docFromDB(dc)
            dc.doc.turn_on = ''
            dc.save()

