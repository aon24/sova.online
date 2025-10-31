# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
'''
from arm.api.forms.formTools import style, _div, _field, _btnD, labelc
from arm.api.forms.classPage import Page
from arm.tools.DC import swell

import json

# *** *** ***


class arm_filter(Page):
    '''
    Форма задает фильтры сессий в ЛК
    '''
    _VIEW_ = 1
    _PAGE_ = 1

    def __init__(self, request):
        self.title = 'colors'
        self.form = 'arm_filter'
        self.jsCssUrlEdit = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        super().__init__(request)

    def page(self, request):

        YN = ['Да|Y', 'Нет|N']
        bogySt = _div(name='filterSt', children=[
            labelc('Допуск разрешен'),
            _field('filterAllow3', 'chb3', YN, xValue='Y'),

            self.sep,
            labelc('Скрыть прошедшие'),
            _field('filterPlan3', 'chb3', YN, xValue='Y', noEmpty=1),

            self.sep,
            labelc('Был на занятии'),
            _field('filterWas3', 'chb3', YN),

            self.sep,
            labelc('Оплачено'),
            _field('filterPayment3', 'chb3', YN,),

            self.sep,
            labelc('Эссе-консультант'),
            _field('filterEC3', 'chb3', ['Эс|E', 'К‑т|C'],),

            self.sep,
            labelc('Дана обр. связь'),
            _field('filterFeedBack3', 'chb3', YN),

            self.sep,
            # show/hide filterEvent3
            _field('showEvent3', 'chb', ['▼\xa0Мероприятия\xa0▼', '▼\xa0Фильтр\xa0событий\xa0▼'],  # ►
                   chbView='change',
                   className='label labelc'),

            _field('filterEvent3', 'band', swell('shortEvents'), recalcText=1,
                   **style(margin='auto', borderSpacing=2, width='auto', border='0 solid #fff', borderTopWidth=1),
                   itemStyle=dict(width=65, borderRadius=12),
                   title='выберите событие',
                   name='filterEvent3',
                   rowLength=2
                   ),
        ])

        bogyCL = _div(name='filterCL', **style(textAlign='center'), children=[
            labelc('Расписание'),
            _field('scheduleChoosing', 'band', [],
                   **style(textAlign='center', padding='0 3px'),
                   className='newBandRed', xValue='Y', recalcText=1),

            self.sep,
            labelc('Скрыть прошедшие'),
            _field('filterPlanCL', 'chb3', YN, xValue='Y', noEmpty=1),

            # self.sep,
            # labelc('Допуск разрешен'),
            # _field(f'filterAllowCL', 'chb3', YN, xValue='Y'),

            self.sep,
            # show/hide showEventCL
            _field('showEventCL', 'chb', ['▼\xa0Мероприятия\xa0▼', '▼\xa0Фильтр\xa0событий\xa0▼'],
                   chbView='change',
                   className='label labelc'),

            _field('filterEventCL', 'band', swell('shortEvents'), recalcText=1,
                   **style(margin='auto', borderSpacing=2, width='auto', border='0 solid #fff', borderTopWidth=1),
                   itemStyle=dict(width=65, borderRadius=12),
                   title='выберите событие',
                   name='filterEventCL',
                   rowLength=2
                   ),
        ])

        return _div(className='color-head', **style(padding='2px 0', border='1px solid #fff'),
                    children=[
                        bogySt,
                        bogyCL,
                        self.sep,
                        _btnD('Закрыть', 'hideFilter', className='btnGreen'),
                ])

    # *** *** ***
    def queryOpen(self, r):
        dcUK = r.dcUK
        sheduleList = ['Полное|All']
        if 'куратор' in dcUK._role:
            sheduleList.append('Куратор|C')
        if 'преподаватель' in dcUK._role:
            sheduleList.append('Преподаватель|L')
        sheduleList.append('Сотрудник|S')
        dcUK.doc.sheduleList = json.dumps(sheduleList)

    # *** *** ***
