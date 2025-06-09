# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well, swell
from ..formTools import style, _div, _field, _btnDel, _btnEdit, _btnNew
from ..classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***

class v_students(Page):
    '''
    button "Студенты по гр."
    '''
    title = 'Студенты'
    dbAlias = 'nv_Profile'
    leftWidth = 105
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']

        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        if not dcUK._staff:
            return '{}'

        if dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)
        elif dcUK.cmd == 'getGroups':
            if dcUK.status == '0':
                data = [k for k in swell('groups') if k.endswith('active')]
            elif dcUK.status == '1':
                data = [k for k in swell('groups') if k.endswith('closed')]
            else:
                data = swell('groups')
        else:
            # '/api/well?clues=groups'
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
        self.leftList = _field('leftList', 'band', [])

        return self.shamrock(addUrl='&status={upList}')

    # *** *** ***

    def getView(self, dcUK):
        grId = (dcUK.selected + '|').split('|')[1]  # 2022-6/Дн|65|active
        mainDocs = []

<<<<<<< HEAD
        for dc in well('students_grId', grId):
            if dc.status == 'active':
                color = '#000'
            else:
                color = '#aaa'

            title = _div(f"{dc.full_name}\n{dc.phone} ({dc.D('_created')})", className='mCell', s2=1, br=1, **style(width='100%', color=color, letterSpacing=1))
=======
        for dc in well('students_grId',grId):
            if dcUK.status == '0':
                if dc.status != 'active':
                    continue
            if dcUK.status == '1':
                if dc.status == 'active':
                    continue
            title = _div(f"{dc.full_name}\n{dc.phone}",className='mCell',s2=1,br=1,**style(width='100%',letterSpacing=1))
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
            btnE = _btnEdit('cmdEdit',dc.id)
            btnD = _btnDel('cmdDel',f'mainList|{dc.id}|nv_Profile')

            row = _div(**style(display='grid',placeItems='center start',gridTemplateColumns='1fr auto auto'),
                children=[title,btnE,btnD])
            mainDocs.append([dc.id,row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        r.dcUK.doc.leftList = json.dumps(swell('groups'), ensure_ascii=False)

    # *** *** ***

# *** *** ***
