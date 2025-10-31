# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.first import err
from arm.tools.DC import well, swell
from ..formTools import _span, style, _div, _btnEdit, _field, _br, gridStyle, _btnDel
from ..classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.api.forms.lk_tools import showC, showCC, rightBtnLK
from arm.api.forms.v_lk_curator.v_lk_curator import v_lk_curator

import json

# *** *** ***


class v_schedule(Page):
    '''
    CRM вид рсписание
    Показвает офису расписание с выбором по группе, преподавателю, по куратору, по фамилии
    а также эмулирует работу куратора, т.е. офис может создавать расписание для группы
    и контролировать студентов
    '''
    title = 'Сессии'
    dbAlias = 'nv_SessionGr'
    leftWidth = 105
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [ f'/api/jsv?forms/{self.form}/{self.form}.js']
        
        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        if not dcUK._staff:
            return '{}'

        data = []
        if dcUK.cmd == 'getSelected':
            if dcUK.uplist == '2':  # Куратор+
                data = v_lk_curator.getView(self, dcUK)
            elif dcUK.view == 'l' or dcUK.upList == '1':  # События / ФИО
                data = self.getView(dcUK)
            else:
                data = showCalendar(dcUK)

        elif dcUK.cmd == 'showCalendar':
            data = showCalendar(dcUK)

        elif dcUK.cmd == 'changeLL':
            if dcUK.filter == '0':
                data = list(swell('events'))
                data.insert(0, 'Все|')
            elif dcUK.filter == '1':
                data = swell('куратор2')
            elif dcUK.filter == '2':
                data = swell('преподаватель2')
        elif dcUK.cmd == 'changeLLCP':
            data = swell('sessionsGr_GrId_band', dcUK.group) or []
            data = [s for s in data if s.endswith('|active') or dcUK.status != 'A']

        # CH shedule
        elif dcUK.cmd == 'changeUp':
            if dcUK.uplist == '1':
                if dcUK.filter == '0':
                    data = list(swell('events'))
                    data.insert(0, 'Все|')
                elif dcUK.filter == '1':
                    data = swell('куратор2')
                elif dcUK.filter == '2':
                    data = swell('преподаватель2')

            else:
                ag = []
                for s in swell('groups'):
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
        if not self._staff:
            return _div('denied')

        ls = ['Расписание', 'События / ФИО', 'Куратор+']
        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
            _field('upList', 'band', ls, **style(margin='auto', width='auto')),
            _field('cPlus', 'band', [], className='bandIB', name='cPlus', recalcText=1),
        ])

        self.viewbar = self.makeViewbar(
            rightBtn=[
                _div(name='viewbar2', **style(flex=1)),
                _field('filter', 'band', ['События', 'Куратор', 'Преподаватель'],
                    name='viewbar2',
                    **style(display='block', margin='auto'),
                    className='radioBand'),

                *rightBtnLK('', na='viewbar1'),

                _div(name='cPlus',
                    children=v_lk_curator.setButtons,  # video+, video-... etc
                    ** style(display='flex', placeItems='center start', position='absolute', top=0, left=107)
                ),
            ],
            **gridStyle('1px 1fr', borderWidth='0 0 2px 0', background='transparent'))

        # слева экрана список групп для курса 'cmd=well&clues=allGroups'
        self.leftList = _field('leftList', 'band', [], name='viewbar1')  # , className='list3str')

        url = '&'.join([
            'form=v_schedule',
            'cmd=getSelected',
            'selected={leftList}',
            'status={status}',
            'filter={filter}',
            'upList={upList}',
            'view={changeView}',
            'plan={plan}' # закомментирован (было "планируемые/все"
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
                if dcUK.status == '0' and sgr.status != 'active':  # кнопка работе
                    continue

                group = well('groups_groupId', sgr.nvgroup_id)
                sLeft = dcUK.selected
                if dcUK.filter == '0' and sLeft and sLeft != sgr.nvEvent:  # filter: 'События'
                    continue
                if dcUK.filter == '1' and sLeft != sgr.curator.partition('|')[2]:  # filter: 'Куратор'
                    continue
                if dcUK.filter == '2' and sLeft != sgr.lector.partition('|')[2]:  # filter: 'Преподаватель'
                    continue

                title = self.getRef(sgr, group)
                row = _div(**gridStyle('1fr auto', placeItems='center start'),
                    children=[title, _btnEdit('cmdEdit', sgr.id)])
                mainDocs.append([sgr.id, row])

            return {'mainDocs': mainDocs, 'refsDocs': None}

        # *** by Groups

        if not dcUK.selected:
            return {'mainDocs': [['all','Группы не найдены'],],'refsDocs': None}

        grId = dcUK.selected

        if '-' in grId:
            ls = well('sessionsGr_All')
        else:
            ls = well('sessionsGr_GrId', grId) or []
            ls.sort(key=lambda x: x.date_begin)

        for sgr in ls:
            if dcUK.status == '0' and sgr.status != 'active':
                continue

            group = well('groups_groupId', sgr.nvgroup_id)
            title = self.getRef(sgr, group)
            btnD = _btnDel('deleteSessionGr', f'{sgr.id}|\n{group} ({sgr.d2})\n{sgr.title}')  # удалить док из вида mainList

            row = _div(**gridStyle('1fr auto auto', placeItems='center start'),
                children=[title, _btnEdit('cmdEdit', sgr.id), btnD])
            mainDocs.append([sgr.id, row])
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
            _span(f' {group.title} ', **style(color='#840', fontWeight='bold')),
            _span(f'(К: {curator} / Л: {lectors}) ',**style(color='#840')),
            _br(),
            _span(f'{vid}: {sgr.title}',**style(color='#555')),
        ], className='rCell')

# *** *** ***


def showCalendar(dcUK):
    dcUK.dateZ_id = 'dateZ_'
    if dcUK.view == 'k1':  # 'к1', 'к2', 'эскиз', 'спис'
        data = showCC(dcUK)  # календарь
    elif dcUK.view == 'k2':
        data = showCC(dcUK)  # календарь
    else:
        data = showC(dcUK)  # эскизы

    return data

# *** *** ***
