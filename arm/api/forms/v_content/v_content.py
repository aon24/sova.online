# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well, swell
from arm.api.forms.formTools import style, _div, _field, _btnDel, _btnEdit, _btnCopy
from arm.api.forms.classPage import Page
from arm.api.forms.lk_tools import showCourse
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_content(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [
            f'/api/jsv?forms/{self.form}/{self.form}.js',
            f'/api/jsv?forms/SessionTmpl/SessionTmpl.js',
        ]
        self.title = 'Программа'
        self.noCaching = True
        self.leftWidth = 115
        self.dbAlias = 'nv_SessionTmpl'
        super().__init__(request)

    def getData(self, dcUK):
        if not (dcUK._staff or 'преподаватель' in dcUK._role):
            return '{}'

        if dcUK.cmd == 'showC':
            if dcUK.view != '0':
                data = showCourse(dcUK)
            else:
                data = self.getView(dcUK)

        elif dcUK.cmd == 'getLectors':
            data = set()
            for the in well('sessionTmpl_nve', 'all'):
                if dcUK.nve.partition('|')[2] == the.nvEvent:
                    [data.add(x) for x in the.lector.split('\n') if x.strip()]
            data = sorted(data)
            data.insert(0, 'Все')
        else:
            data = 'invalid cmd'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        events = swell('events')  # названия мерориятия | code

        lsNew = []
        for c in events:
            lsNew.append(c.partition('|')[2])

        self.leftList = _field('leftList', 'band', [], className='list3str')

        self.viewbar = self.makeViewbar(
            leftBtn=[_field('view', 'band', ['спис', 'эскиз'], className='radioBand', title='список/эскизы',)],
            rightBtn=[_field('status', 'band', ['актив', 'архив'], className='radioBand', **style(marginLeft='auto '))],
        )

        # 1 вверху экрана список мероприятий
        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
            _field('upList', 'band', events, recalcText=1, rowLength=1, className='event', addBtn='cmdNew', blocking=3),
        ])

        url = '/api/getData?form=v_content&cmd=showC&nve={upList}&lector={leftList}&status={status}&view={view}'
        self.mainList = _div(children=[
            _field('mainList', 'view', name='mainList', limit=100000, url=url, previewUrl=f'dbAlias={self.dbAlias}'),
            _field('showCourse', 'json', name='showCourse')
        ])
        return self.shamrock()

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []
        nve = dcUK.nve.partition('|')[2]
        for the in well('sessionTmpl_nve', nve):
            if dcUK.status == '0':  # кнопка работе
                if the['status'] != 'active':
                    continue
            else:
                if the['status'] == 'active':
                    continue

            if dcUK.lector != 'Все' and dcUK.lector not in the.lector:
                continue

            title = _div(f'{the.title}', br=1, className='mCell', **style(width='100%', letterSpacing=1))
            pk = the['pk']
            btnE = _btnEdit('cmdEdit', pk)
            btnC = _btnCopy('cmdNewCopy', pk)
            btnD = _btnDel('cmdDel', f'mainList|{pk}|nv_SessionTmpl')  # удалить док из вида mainList

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto'),
                children=[title, btnE, btnC, btnD])
            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        r.dcUK.doc.upList = swell('events')[0]

    # *** *** ***

# *** *** ***
