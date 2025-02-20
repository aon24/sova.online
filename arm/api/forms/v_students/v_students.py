# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well
from ..formTools import style, _div, _field, _btnDel, _btnEdit, _btnNew
from ..classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***

class v_students(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Студенты'
        self.dbAlias = 'nv_Profile'
        self.leftWidth = 105
        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        if dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)
        else:
            data = f'invalid cmd: {dcUK.cmd}'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        self.viewbar = self.makeViewbar(
            leftBtn=[_btnNew(self.dbAlias)],
            rightBtn=[_field('upList', 'band', ['актив', 'архив', 'все'], className='radioBand')]
        )

        self.upField = _div(children=[
            _div(className='toolbar',children=[toolbar.close_]),
        ])
        self.leftList = _field('leftList', 'band', '/api/well?clues=groups')

        return self.shamrock(addUrl='&status={upList}')

    # *** *** ***

    def getView(self, dcUK):
        grId = (dcUK.selected + '|').split('|')[1]  # 2022-6/Дн|65|active
        mainDocs = []

        for dc in well('students_grId',grId):
            if dcUK.status == '0':
                if dc.status != 'active':
                    continue
            if dcUK.status == '1':
                if dc.status == 'active':
                    continue
            title = _div(f"{dc.full_name}\n{dc.phone}",className='mCell',s2=1,br=1,**style(width='100%',letterSpacing=1))
            btnE = _btnEdit('cmdEdit',dc.pk)
            btnD = _btnDel('cmdDel',f'mainList|{dc.pk}|nv_Profile')

            row = _div(**style(display='grid',placeItems='center start',gridTemplateColumns='1fr auto auto'),
                children=[title,btnE,btnD])
            mainDocs.append([dc.pk,row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, dcUK):
        dcUK.doc._view_ = 1
        dcUK.doc.leftList = json.dumps(well('groups'), ensure_ascii=False)

    # *** *** ***

# *** *** ***
