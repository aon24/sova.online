'''
Created on 2024

@author: aon24
'''
from arm.tools.common import now, checkBusy
from arm.tools.DC import DC
from arm.tools.first import snd, err
from arm.tools.dbToolkit.Book import snoDB
from arm.tools.dbToolkit.DJ import docFromDB

import importlib
import traceback

# *** *** ***


def makeReport(oneReport):
    '''
    создает в базе отчетов заготовку отчета
    вызывается из v_reports, если выбрано "сейчас 1 раз"(oneReport - dc-obj from v_reports)
    заготовка аналогична агенту с расписанием "выполнить сейчас 1 раз"
    '''
    report = DC()
    for k in oneReport.keys():
        l, _, r = k.partition('_')
        if l == 'REPORT':
            report[r] = oneReport[k]

    report.form = 'Report'
    report.title = oneReport.title
    report.domain = oneReport.domain
    report.scheduled = 'now'
    report.turn_on = 1
    report.status = 'active'

    dcuk = DC(dbAlias='nv_reports_Report', fullName='makeReport')
    report.docNo = snoDB(dcuk)
    dcuk.doc = report
    if dcuk.save():
        snd(oneReport.report_title, cat='Report-job-now created')
    else:
        err('Report-save-error', cat='Report-job-now NOT created')

# *** *** ***


@checkBusy  # Декоратор, блокирующий повторный вызов функции до ее завершения.
def startReport(agent):
    """
    вызывается из amgr
    в параметре report либо задание из расписания (form = 'Module'),
    либо одноразовый отчет (form = 'Report' и scheduled=='now' and turn_on = 1)
    """
    cat = 'Report run'
    path = f'nv_reports.{agent.domain}.{agent.module or agent.report_module}'
    snd(f'Start(import_module): "{path}"\nReport.title: "{agent.title}"', cat=cat)

    if agent.form == 'Module':
        # вызов по расписанию. Надо создать отчет
        report = DC()
        for k in agent.keys():
            l, _, r = k.partition('_')
            if l == 'REPORT':
                report[r] = agent[k]

        report.form = 'Report'
        report.domain = agent.domain
        report.title = agent.title
        report.status = 'active'
        report.starting_time = now('-')
        report.lmRef = agent.id

        # создаем пустой отчет
        dcuk = DC(dbAlias='nv_reports_Report', fullName=cat)
        report.docNo = snoDB(dcuk)
        dcuk.doc = report
        try:
            report.id = dcuk.save().id
            snd(report.title, cat='Report created')
        except Exception:
            return err('Report-save-error', cat='Report NOT created')

    else:  # одноразовый отчет.Он уже создан и сохранен в makeReport
        report = agent

    # перезаписываем то, что для amgr
    dcuk = DC(dbAlias='nv_reports_Report', unid=agent.id, fullName=cat)
    docFromDB(dcuk)

    agent._run = ''
    if agent.SCHEDULED == 'now':  # одноразовый отчет.Он уже создан и сохранен в makeReport
        agent.TURN_ON = ''  # 1 раз и нефиг
        agent.starting_time = now('-')

    dcuk.doc = agent
    if not dcuk.save():
        return err('Module-save-error', cat='Report NOT created')

    try:
        mmm = importlib.import_module(path)
        importlib.reload(mmm)

        # *** make !!!

        htmlList = mmm.main(report) or []

        # ***

        report.end_time = now('-')
        dcuk = DC(dbAlias='nv_reports_Report', unid=report.id, fullName=cat)
        docFromDB(dcuk)
        dcuk.doc = report
        dcuk.save()

        for html in htmlList:
            ref = DC(dbAlias='nv_reports_Report', fullName=cat)
            ref.doc = DC(ref=report.id, form='html', status='active')
            ref.doc.main = html.main
            ref.doc.title = html.title or report.title  # заголовок в виде
            ref.doc.jsCss = html.jsCss
            ref.save()

        snd(f'Finish: {report.title}', cat=cat)

    except Exception as ex:
        s = f'{report.title}(path:"{path}")\n{ex}\n{traceback.format_exc()}'
        report.log += s
        err(s, cat=cat)
        dcuk = DC(dbAlias='nv_reports_Report', unid=report.id, fullName=cat)
        docFromDB(dcuk)
        dcuk.doc = report
        dcuk.save()

        if report.lmRef:
            dc = DC(dbAlias='nv_lm_Module', unid=report.lmRef, fullName=cat)
            docFromDB(dc)
            dc.doc._run = dc.doc.turn_on = ''
            dc.save()

