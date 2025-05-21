# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well, swell
from arm.tools.first import err
from arm.api.forms.formTools import style, _div, _search, _field, _btnDel, _btnEdit, _btnNew, _btnView
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_more(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Лендинг'
        self.dbAlias = 'draft'
        self.leftWidth = 105
        self.noCaching = True

        super().__init__(request)

    def getData(self, dcUK):
        try:
            if dcUK.cmd == 'getSelected':
                data = self.getView(dcUK)
            elif dcUK.cmd == 'getLeftList':
                project = set()
                [project.add(dc.project) or '-?-' for dc in well('landing') if dc.key == dcUK.key or dcUK.key == 'все']
                project = sorted(project)
                project.append('все')
                data = project
            else:
                data = f'invalid cmd: {dcUK.cmd}'
        except Exception as ex:
                err(f'{ex}', cat='arm.getData.getView')
                data = {'mainDocs': [('123', f'ERROR: {ex}'), ], 'refsDocs': []}
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        self.upField = _div(children=[
            _div(className='toolbar',children=[toolbar.close_]),
            _field('key', 'band', swell('3dKeys') + ['все'], recalcText=1, **style(margin='auto', display='table', width='auto'))
        ])

        self.leftList = _field('leftList', 'band', [], className='list3str')

        self.viewbar = self.makeViewbar(
            leftBtn=[_btnNew('a_design'), _btnNew('a_more')],
            rightBtn=_search()
        )

        return self.shamrock(addUrl='&key={key}')

    # *** *** ***

    def getView(self, dcUK):
        project = dcUK.selected
        key = dcUK.key
        mainDocs = []

        for cls in sorted(well('landing'), key=lambda dc: dc.modified or dc.created, reverse=True):
            pk = cls.unid

            if project != 'все' and project != cls.project:
                continue
            if key != 'все' and key != cls.key:
                continue

            title = _div(f"{cls.key} -- {cls.project} -- {cls.pageName}\n{cls.pageSize} ({cls.modified or cls.created})",
                className='mCell', s2=1, br=1, **style(width='100%', paddingLeft=2, letterSpacing=1))

            btnV = _btnView('cmdView', pk)
            btnE = _btnEdit('cmdEdit', pk)
            btnD = _btnDel('cmdDel', f'mainList|{pk}|draft')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto'),
                children=[title, btnV, btnE, btnD])
            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        r.dcUK.doc._view_ = 1

# *** *** ***
