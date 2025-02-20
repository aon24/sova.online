# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from ..formTools import style,_div,_field,_btnDel,_btnEdit,_btnNew
from ..classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.tools.DC import well

import json

# *** *** ***


class v_groups(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Группы'
        self.dbAlias = 'nv_NVGroup'
        self.leftList = None

        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        if dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)
        else:
            data = 'invalid cmd'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        self.upField = _div(className='toolbar',children=[toolbar.close_])
        self.viewbar = self.makeViewbar(name='viewbar2',
            leftBtn=[_btnNew(self.dbAlias,cmd='newGroup')],
            rightBtn=[_field('status','band',['актив','архив','все'],className='radioBand')])

        return self.shamrock(addUrl='&status={status}')

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []

        for group in well('groups_groupId').values():
            pk = group.pk

            if dcUK.status != '2':  # 2 - все гр без учета курса и статуса
                if dcUK.status == '0':  # кнопка в работе
                    if group.status != 'active':
                        continue
                else:
                    if group.status == 'active':
                        continue

            curator = group.curator.partition('|')[0]
            title = _div(f'{group.title} {group.D("date_begin")} {group.D("date_end")}\nКуратор: {curator}',
                s2=1, br=1, className='mCell', **style(width='100%', letterSpacing=1, height=37))

            btnE = _btnEdit('cmdEdit', pk)
            btnD = _btnDel('cmdDel', f'mainList|{pk}|nv_NVGroup')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                children=[title, btnE, btnD])
            mainDocs.append([pk, row, group.title])

        mainDocs = [ [m[0], m[1]] for m in sorted(mainDocs, key=lambda x: x[2], reverse=True)]
        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, dcUK):
        dcUK.doc._view_ = 1

# *** *** ***
