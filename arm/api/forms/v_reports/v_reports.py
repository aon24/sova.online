# -*- coding: utf-8 -*-
'''
AON 9 mar 2018

'''
from arm.api.forms.formTools import _btnNew, _btnEdit, style, gridStyle, _btnD, _field, labField, labell, labeldc, _div, _btnDel, _btnView
from arm.tools.DC import DC, DCC, well, swell
from arm.tools.first import err
from arm.tools.common import today
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.tools.makeReport import makeReport

from django.http import HttpResponse

from importlib import import_module, reload
from datetime import datetime, timedelta
import json

# *** *** ***

class v_reports(Page):
    domain = 'rf_nv'
    title = 'Отчеты'
    leftWidth = 350
    noCaching = True

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js',
                         f'/api/jsv?forms/{self.form}/{self.form}.css'
                        ]

        self.upField = _div(className='toolbar', children=[toolbar.close_])
        self.viewbar = self.makeViewbar(
            expand='first',
            **gridStyle('300px auto'),
            leftBtn=[
                _btnNew(name='newLM'),
                _field('db', 'band', ['отчеты', 'расписание', 'агенты'], **style(margin='auto'), className='radioBand')
            ],
            rightBtn=[
                _div('собранные отчеты', className='bandItem bandItem-sel',
                   name='db0',
                   **style(font='normal 14px Verdana, Arial', height=28, color='#036')
                ),
                _div('отчеты по расписанию', className='bandItem bandItem-sel',
                   name='db1',
                   **style(font='normal 14px Verdana, Arial', height=28, color='#036')
                ),
                _field('agentView', 'band', ['агенты', 'результаты агентов'], name='db2', **style(margin='auto', width='auto')),
            ],
        )

        super().__init__(request)

    # *** *** ***

    def putData(self, dcUK, buf):
        try:
            dc = DC(domain=self.domain)
            for kv in buf.split('&'):
                k, _, v = kv.partition('=')
                dc[k] = v

            if dcUK.cmd == 'startReport':
                makeReport(dc)
                return HttpResponse('OK')

            elif dcUK.cmd == 'scheduleReport':
                dc.report = 1
                dc.form = 'Module'
                dc.turn_on = 1
                dc.status = 'active'
                dcUK = DC(dbAlias='nv_reports_Report')
                dcUK.doc = dc
                dcUK.save()
                return HttpResponse('OK')

            else:
                err(f'Unknown cmd: {dcUK.cmd}', cat=self.form)
                return HttpResponse(f'PutData for {self.form}. Unknown cmd: {dcUK.cmd}', None, 200)

        except Exception as ex:
            s = f'PutData for form "{self.form}" (cmd={dcUK.cmd}): {ex}'
            err(s, cat=self.form)
            return HttpResponse(s, None, 200)

    # *** *** ***
    def getData(self, dcUK):
        if dcUK.cmd == 'getSelected':
            if dcUK.db == '0':  # reports
                data = self.getView(dcUK, dba='reports')
            elif dcUK.db == '1':  # reports and schedule
                data = self.getViewLM(dcUK, dba='reports')
            else:  # agents
                if dcUK.agentView == '0':  # список агентов
                    data = self.getViewLM(dcUK, dba='modules')
                else:  # результаты
                    data = self.getView(dcUK, dba='modules')
        else:
            data = 'invalid cmd: {dcUK.cmd}'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***
    
    def page(self, request):
        repList = [
            DCC(
                title=' Все собранные отчеты',
                comment='\nДля сбора нового отчета выберите нужную категорию'
        )]

        mmm = reload(import_module(f'nv_reports.rf_nv.description'))
        for r in mmm.reportList(*oldQuar(0)):  # oldQuar(0) - от начала текущего квартала до today
            repList.append(DCC(r))
        repListKeys = [r.title for r in repList]

        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
        ])

        rep = _div(**style(background='#00ffff10', marginBottom=10), name='rep', children=[

            _field('title', 'list', dropList=repListKeys),
            _div(children=[self.setReport(i, x) for i, x in enumerate(repList)]),

            _div(name='shedule', children=[
                *labField('Расписание', 'SCHEDULED', 'lbsd', swell('scheduled'), xValue='now', alias=1, **style(marginRight=15)),
                _div(**gridStyle('1fr 10px 1fr'), name='dayTime', children=[
                    labeldc('Время'),
                    _div(),
                    labeldc('День'),
                ]),
                _div(**gridStyle('1fr 10px 1fr 15px'), name='dayTime', children=[
                    _field('SCHEDTIME', 'lbsd', '', alias=1),
                    _div(),
                    _field('SCHEDDAY', 'lbsd', '', alias=1),
                    _div(),
                ]),
                _btnD('Собрать отчет', 'startReport', name='startReport', className='rsvTop', **style(width=180, margin='10px auto 20px')),
                _btnD('Добавить отчет в расписание', 'scheduleReport', className='rsvTop', name='dayTime', **style(width=240, margin='10px auto')),
            ])
        ])

        sched = _field('category', 'list', ['включен', 'выполняется', 'все'], name='sched', className='list33str')
        # sched = _field('category', 'band', ['включен', 'выполняется', 'все'], name='sched', className='list33str', recalcText=1)
        self.leftList = _div(children=[rep, sched])

        return self.shamrock(expand='first', focus='', addUrl='&agentView={agentView}&category={category}&db={db}&title={title}')

    def getView(self, dcUK, dba):
        mainDocs = []
        ids = []
        if dba == 'reports':
            dbAlias = 'nv_reports_Report'
        else:
            dbAlias = 'nv_lm_Module'

        for m in well(dba):
            if m.form.lower() != 'report':
                continue

            pk = m.pk

            if dba == 'reports' and dcUK.title not in ['Все собранные отчеты', m.title]:
                continue

            ids.append(pk)
            title = _div(f"{m.docNo}. {m.title}\n{m.starting_time} => {m.end_time}",
                className='mCell', s2=1, br=1, **style(width='100%', paddingLeft=2, letterSpacing=1))

            btnV = _btnEdit('cmdEdit', f'unid={pk}&dbAlias={dbAlias}&form=Report')
            btnD = _btnDel('cmdDel', f'mainList|{pk}|{dbAlias}')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                children=[title, btnV, btnD])
            mainDocs.append([pk, row])

        refsDocs = {}
        for o in well(dba):
            if o.form != 'html' or o.ref not in ids:
                continue

            refsDocs[o.ref] = refsDocs.get(o.ref, [])
            refsDocs[o.ref].append([o.pk, _div(o.title or '-', className='rCell', **style(marginLeft=20, width='100%'))])

        return {'mainDocs': mainDocs, 'refsDocs': refsDocs}

    def queryOpen(self, r):
        r.dcUK.doc._view_ = '1'

# *** *** ***

    def setReport(self, i, r):
        if not r.listbox:
            return _div(name=f'krd_{i}', children=[
                _div(r.comment, **style(textAlign='center', font='normal 9pt Verdana', color='#555'), br=1)
            ])

        ls = [
            labeldc('параметры для сбора отчета', **style(marginTop=10)),
            _field(f'reportName_{i}', 'list', r.listbox, saveAlias=1, listItemClassName='repName',),
        ]

        if r.addList:
            ls += [
                labeldc('доп. параметры для сбора отчета', **style(marginTop=10)),
                _field(f'addList_{i}', 'list', r.addList, saveAlias=1, listItemClassName='repName')
            ]

        if r.who:
            ls += [
                labeldc('Выбрать фамилии', **style(marginTop=10)),
                _field(f'who_{i}', 'lbmd', r.who, saveAlias=1)
            ]

        if 'DT2' not in r.keys():
            if r.dt1_label:
                ls.append(labeldc(r.dt1_label, **style(marginTop=10)))
            ls.append(_field(f'dt1_{i}', 'dt', **style(margin='auto'), xValue=r.dt1))
        else:
            ls += [
                labeldc('задать квартал в качестве периода', **style(marginTop=10)),
                qartButton,
                _div(**gridStyle('auto auto', marginTop=10), children=[
                    labell('Начало периода'),
                    labell('Конец периода')
                ]),
                _div(**gridStyle('auto auto'), children=[
                    _field(f'dt1_{i}', 'dt', xValue=r.dt1),
                    _field(f'dt2_{i}', 'dt', xValue=r.dt2)
                ])
            ]
        if r.diff:
            ls += [
                _div(**gridStyle('1fr auto auto auto 1fr', marginTop=10), children=[
                    _div(),
                    labeldc('↓\xa0перенести даты \xa0', **style(font='normal 9pt Arial')),
                    _btnD('↓', 'p2', f'{i}', title='перенести с заменой года', className='svTop', **style(width='5mm', color='blue')),
                    labeldc('\xa0 с заменой года\xa0↓', **style(font='normal 9pt Arial')),
                    _div(),
                ]),
                labeldc('Предыдущий период'),
                _div(**gridStyle('auto auto'), children=[
                    _field(f'dt3_{i}', 'dt', xValue=r.dt3),
                    _field(f'dt4_{i}', 'dt', xValue=r.dt4)
                ])
            ]

        ls.append(_field(f'module_{i}', 'fd', xValue=r.module, **style(font='normal 9pt Verdana', color='#555')))
        ls.append(_div(f':{r.comment}', **style(display='inline', font='normal 9pt Verdana', color='#555'), br=1))

        return _div(name=f'krd_{i}', children=ls)

# *** *** ***

    def getViewLM(self, dcUK, dba):
        category = dcUK.category

        mainDocs = []
        if dba == 'reports':
            dbAlias = 'nv_reports_Report'
        else:
            dbAlias = 'nv_lm_Module'

        for m in well(dba):
            if m.form != 'Module':
                continue

            pk = m.pk

            if category == 'выполняется' and not m.run:
                continue
            if category == 'включен' and not m.turn_on:
                continue

            tit = m.title.replace('\n', '-')
            if m._run:
                color = 'blue'
            elif m.turn_on:
                color = 'black'
            else:
                color = 'gray'
            title = _div(f"{tit}\n{m.starting_time} => {m.end_time}",
                className='mCell', s2=1, br=1, **style(width='100%', color=color, paddingLeft=2, letterSpacing=1))

            btnV = _btnEdit('cmdEdit', f'unid={pk}&dbAlias={dbAlias}&form=Module')
            btnD = _btnDel('cmdDel', f'mainList|{pk}|{dbAlias}')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                children=[title, btnV, btnD])
            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

# *** *** ***


def oldQuar(n, sep='-'):
    y = datetime.today().year
    q = int((datetime.today().month - 1) / 3)
    m = (q * 3) + 1
    qua = f'{y}-{m:02d}-01'
    if n > 0:
        dt1, dt2 = monthSub(qua, n * 3), monthSub(qua, (n - 1) * 3 + 1, -1)
        if sep == '-':
            return dt1.strftime('%Y-%m-%d'), dt2.strftime('%Y-%m-%d')
        else:
            return dt1.strftime('%d.%m.%Y'), dt2.strftime('%d.%m.%Y')
    else:
        if sep != '-':
            qua = f'01.{m:02d}.{y}'
        return qua, today(sep)

# *** *** ***


def monthSub(sourDate, n, day=0):
    start_date = datetime.strptime(sourDate, "%Y-%m-%d")
    sour_day = start_date.day

    for i in range(0, n):
        start_date = start_date.replace(day=1) - timedelta(days=1)

    if day == 0:
        start_date = start_date.replace(day=sour_day)
    elif day > 0:
        start_date = start_date.replace(day=day)

    return start_date

# *** *** ***


qartButton = _div(**gridStyle('auto ' * 7, width='100%', placeItems='center start'))
qartButton['children'] = []
for j in range(7):
    qartButton['children'].append(_btnD(f'-{j} кв' if j else 'кв', 'setQuar', '%s|%s' % oldQuar(j),
        title='с %s по %s' % oldQuar(j, '.'), className='rsvTop', **style(width=40)))

