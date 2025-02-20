# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.first import err
from arm.tools.DC import well
from ..formTools import _span, style, _div, _btnEdit, _field, _br, gridStyle, _btnDel
from ..classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.api.forms.lk_tools import showC, showCC
from arm.api.forms.lk_curator.lk_curator import lk_curator

import json
from datetime import datetime, timedelta

# *** *** ***


class v_schedule(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [ f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Сессии'
        self.dbAlias = 'nv_SessionGr'

        self.leftWidth = 105
        
        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        data = []
        if dcUK.cmd == 'getSelected':
            if dcUK.uplist == '2':
                data = lk_curator.getView(self, dcUK)
            elif dcUK.view == '3' or dcUK.upList == '1':
                data = self.getView(dcUK)
            else:
                data = showCalendar(dcUK)

        elif dcUK.cmd == 'showCalendar':
            data = showCalendar(dcUK)

        elif dcUK.cmd == 'changeLL':
            if dcUK.filter == '0':
                data = list(well('events'))
                data.insert(0, 'Все')
            elif dcUK.filter == '1':
                data = well('куратор2')
            elif dcUK.filter == '2':
                data = well('преподаватель2')
        elif dcUK.cmd == 'changeLLCP':
            data = well('sessionsGr_GrId_band', dcUK.group) or []
            if dcUK.status == '0':
                data = [s for s in data if s.endswith('|active')]
            else:
                data = [s for s in data if s.endswith('|closed')]

        # CH shedule
        elif dcUK.cmd == 'changeUp':
            if dcUK.uplist == '1':
                if dcUK.filter == '0':
                    data = list(well('events'))
                    data.insert(0, 'Все')
                elif dcUK.filter == '1':
                    data = well('куратор2')
                elif dcUK.filter == '2':
                    data = well('преподаватель2')

            else:
                ag = []
                for s in well('groups'):
                    ls = s.split('|')  # 🌆🌃🌝🌚🌛🌖🌠
                    if ls[2] == 'active':
                        title = ls[0].replace('/День', '🌞').replace('/Дн', '🌞').replace('/Веч', '🌚')
                        data.append(f'{title}|{ls[1]}')
                        ag.append(ls[1])
                if dcUK.uplist == '0':
                    data.insert(0, f'Все группы|{"-".join(ag)}')
        else:
            data = f'invalid cmd: {dcUK.cmd}'
            err(f'invalid cmd: {dcUK.cmd}', cat='v_sheduled.getData')

        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        ls = ['Расписание в группах', 'События / ФИО', 'Куратор+ (платежи пр.)']
        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
            _field('upList', 'band', ls, **style(margin='auto', width='auto')),
            _field('cPlus', 'band', [], className='bandIB', name='cPlus', recalcText=1),
        ])

        self.viewbar = self.makeViewbar(
            leftBtn=[_field('status', 'band', ['актив', 'архив'], className='radioBand')],
            rightBtn=[
                _field('filter', 'band', ['События', 'Куратор', 'Преподаватель'],
                    name='viewbar2',
                    className='radioBand'),
                _field('changeView', 'band', ['K1', 'K2', 'эскиз', 'спис'],
                    name='viewbar1',
                    className='radioBand',
                    title='календарь/список/эскизы',
                    **style(position='absolute', top=3, right=2)),
                _field('event', 'band', well('shortEvents'), recalcText=1,
                    className='radioBand',
                    title='выберите событие',
                    name='event'),
                _field('plan', 'band', ['Планируемые', 'все'],
                    className='radioBand',
                    name='plan'),
                _div(name='cPlus',
                    children=lk_curator.setButtons,
                    **style(display='flex', placeItems='center start', position='absolute', top=0, left=107)
                ),
            ], **style(placeItems='center center'))

        # слева экрана список групп для курса '/api/well?clues=allGroups'
        self.leftList = _field('leftList', 'band', [], name='viewbar1')  # , className='list3str')

        url = '&'.join([
            '/api/getData?form=v_schedule',
            'cmd=getSelected',
            'selected={leftList}',
            'status={status}',
            'filter={filter}',
            'upList={upList}',
            'view={changeView}',
            'plan={plan}'
        ])
        self.mainList = _div(**style(height='100%'), children=[
            _field('mainList', 'view', name='mainList', limit=100000, url=url, previewUrl=f'dbAlias={self.dbAlias}', expand='first'),
            _field('showCourse', 'json', **style(height='100%'), name='showCalendar')
        ])
        return self.shamrock()

    # ***

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []

        if dcUK.upList == '1':  # upList: 'Расписание в группах', 'События / ФИО|1', 'Куратор+ (платежи пр.)'
            for sgr in well('sessionsGr_All'):
                if dcUK.status == '0':  # кнопка работе
                    if sgr.status != 'active':
                        continue
                elif sgr.status == 'active':
                        continue

                if dcUK.selected != 'Все':
                    sLeft, _, sRight = dcUK.selected.partition('|')
                    if dcUK.filter == '0' and sRight != sgr.nvEvent:  # filter: 'События', 'Куратор', 'Преподаватель'
                        continue
                    if dcUK.filter == '1' and sLeft != sgr.curator.partition('|')[0]:
                        continue
                    if dcUK.filter == '2' and sLeft != sgr.lector.partition('|')[0]:
                        continue

                group = well('groups_groupId', sgr.nvgroup_id).title
                title = self.getRef(sgr, group)
                row = _div(**gridStyle('1fr auto', placeItems='center start'),
                    children=[title, _btnEdit('cmdEdit', sgr.id)])
                mainDocs.append([sgr.id, row])

            return {'mainDocs': mainDocs, 'refsDocs': None}

        # *** by Groups

        if not dcUK.selected:
            return {'mainDocs': [['all','Группы не найдены'],],'refsDocs': None}

        grId = dcUK.selected.partition('|')[2]

        if '-' in grId:
            ls = well('sessionsGr_All')
        else:
            ls = well('sessionsGr_GrId', grId)

        days = 1 if dcUK.plan == '0' else 100000  # не показ эскизы через 1 день после оконч or isEmpty
        yesterday = datetime.now() - timedelta(days=days)
        last = yesterday.strftime("%Y-%m-%d")

        for sgr in ls:
            if dcUK.status == '0':  # кнопка работе
                if sgr.status != 'active':
                    continue
            elif sgr.status == 'active':
                    continue

            dateEnd = sgr.date_end or sgr.date_begin
            if dateEnd < last:
                continue

            group = well('groups_groupId', sgr.nvgroup_id).title
            title = self.getRef(sgr, group)
            btnD = _btnDel('deleteSessionGr', f'{sgr.pk}|\n{group} ({sgr.d2})\n{sgr.title}')  # удалить док из вида mainList

            row = _div(**gridStyle('1fr auto auto', placeItems='center start'),
                children=[title, _btnEdit('cmdEdit', sgr.id), btnD])
            mainDocs.append([sgr.id,row])
        return {'mainDocs': mainDocs,'refsDocs': None}

    # *** *** ***

    def getRef(self, sgr, group):

        dbg = sgr.d2 or '--.-- --.--'
        ls = [x.partition('|')[0] for x in sgr.lector.split('\n')]
        lectors = ','.join([x.partition(" ")[0] for x in ls])
        curator = sgr.curator.partition(" ")[0]
        vid = well('eventsByCode', sgr.nvEvent) or '?'
        duration = sgr.duration or '--:-- --:--'

        return _div(children=[
            _span(f'{dbg} ',**style(fontWeight='bold')),
            _span(duration,**style(color='#840')),
            _span(f' {group} ',**style(color='#840',fontWeight='bold')),
            _span(f'(К: {curator} / Л: {lectors}) ',**style(color='#840')),
            _br(),
            _span(f'{vid}: {sgr.title}',**style(color='#555')),
        ], className='rCell')

    def queryOpen(self, dcUK):
        dcUK.doc._view_ = 1

# *** *** ***


def showCalendar(dcUK):
    dcUK.dateZ_id = 'dateZ_'
    if dcUK.view == '0':  # 'к1', 'к2', 'эскиз', 'спис'
        data = showCC(dcUK)  # календарь
    elif dcUK.view == '1':
        data = showCC(dcUK)  # календарь
    else:
        data = showC(dcUK)  # эскизы

    return data

# *** *** ***
