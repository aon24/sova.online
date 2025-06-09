# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well
from arm.api.forms.formTools import _search,style,_div,_btnDel,_btnEdit,_field
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_payments(Page):
    title = 'Платежи'
    dbAlias = 'nv_Payment'
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.leftList = None

        self.upField = _div(className='toolbar', children=[toolbar.close_])
        self.viewbar = self.makeViewbar(
            rightBtn=_search(),
            leftBtn=[_field('status', 'band', ['актив', 'архив'], className='radioBand')],
        )

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
        return self.shamrock(addUrl='&status={status}&profile={profile}')

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []

        if dcUK.profile:
            if dcUK._staff or dcUK._PROFILEPK == dcUK.profile:
                pass
            elif 'куратор' in self._role:
                pass  # todo: access only for own groups, for other disable
            else:
                return '{}'
            payArr = well('payments_profile', dcUK.profile)  # при вызове из форм Profile/SessionSt
        else:
            if not dcUK._staff:
                return '{}'
            payArr = well('payments')  # при вызове по кнопке "Платежи"

        for pay in payArr:
            if dcUK.status == '0':  # кнопка работе
                if pay.status != 'active':
                    continue
            elif pay.status == 'active':
                continue

            pk = pay.id
            group = well('groups_groupId',pay.nvgroup).title
            ch = pay.cash[:1].upper()
            date = _div(f"{pay.D('pay_date')}\n{ch}: {pay.summa}",
                className='mCell', s2=1, br=1, **style(color='#036'))
            if pay.t1:
                t12 = f'\n{pay.D("t1")}'
                if pay.t2:
                    t12 += f' - {pay.D("t2")}'
            else:
                t12 = ''
            title = _div(f"{pay.fio}\n{pay.phone} ({group}){t12}",
                className='mCell', s2=1, br=1, **style(width='100%', letterSpacing=1))

            if 'куратор' in dcUK._role or dcUK._staff:
                btnE = _btnEdit('cmdEdit',pk)
                btnD = _btnDel('cmdDel', f'mainList|{pk}|nv_Payment')  # удалить док из вида mainList

                row = _div(**style(display='grid',placeItems='center start',gridTemplateColumns='90px 1fr 33px 33px'),
                    children=[date, title, btnE, btnD])
                mainDocs.append([pk, row])

            else:
                row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='90px 1fr'),
                    children=[date, title])
                mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        r.dcUK.doc.profile = r.dcUK.profile

    # *** *** ***

# *** *** ***
