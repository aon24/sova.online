# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well
from arm.api.forms.formTools import _search,style,_div,_btnD,_field,_btnDel,_btnEdit,_btnNew
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_profiles(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js',]
        self.title = 'Профайлы'
        self.dbAlias = 'nv_Profile'
        self.leftWidth = 105
        self.roles = well('role')
        self.roles.insert(0, 'ВСЕ')

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
        self.upField = self.upField = _div(children=[
            _div(className='toolbar',children=[toolbar.close_]),
            _field('status', 'band', ['актив', 'архив', 'все'], recalcText=1, **style(margin='auto', display='table', width='auto'))
        ])

        self.viewbar = self.makeViewbar(
            leftBtn=[_btnNew(self.dbAlias)],
            rightBtn=_search()
        )

        self.leftList = _field('leftList', 'band', self.roles)

        return self.shamrock(addUrl='&status={status}')

    # *** *** ***

    def getView(self, dcUK):
        topStatus = dcUK.status
        mainDocs = []

        for the in well(dcUK.selected.replace('ВСЕ', 'alls')):
            fio, pk, phone, email, status = the.split('|')
            if topStatus != 'Все':
                if topStatus == 'актив' and status != 'active':
                    continue
                if topStatus == 'архив' and status != 'closed':
                    continue

            title = _div(f'{fio}\n{phone} ({email})',  # 'preview', pk,
                className='mCell', s2=1, br=1, **style(width='100%', letterSpacing=1))

            btnPay = _btnD('Р', 'cmdNewPay', pk, className=f'btnIcon mBtn fv2 fv2yes', title='оплачено')
            btnE = _btnEdit('cmdEdit', pk)
            btnD = _btnDel('cmdDel', f'mainList|{pk}|nv_Profile')  # удалить док из вида mainList

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto'),
                children=[title,btnPay,btnE,btnD])
            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, dcUK):
        dcUK.doc._view_ = 1

    # *** *** ***

# *** *** ***
