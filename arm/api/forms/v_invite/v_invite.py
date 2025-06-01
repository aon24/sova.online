'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import swell
from arm.api.forms.formTools import style, _div, _btnEdit, _field, _btnDel, _btnD, _btnNew, _search
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_invite(Page):
    '''
    view for Pofiles with fields 'fest', 'training', 'invite'
    '''
    title = 'Дополнительно'
    dbAlias = 'nv_Profile'
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

        if dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)
        elif dcUK.cmd == 'changeUp':
            data = self.getLeftList(dcUK)
        else:
            data = f'invalid cmd: {dcUK.cmd}'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        ls = ['Тренинг|training', 'Фест|fest', 'Озн.сем|invite']
        self.upField = _div(children=[
            _div(className='toolbar',children=[toolbar.close_]),
            _field('upList', 'band', ls, recalcText=1, **style(margin='auto', width='auto'))
        ])

        self.viewbar = self.makeViewbar(
            leftBtn=[_btnNew(self.dbAlias)],
            rightBtn=_search()
        )

        self.leftList = _field('leftList', 'band', [], name='viewbar1', className='list3str')

        return self.shamrock(addUrl='&upList={upList}')

    # *** *** ***

    def getLeftList(self, dcUK):
        key = dcUK.upList
        left = set()
        for u in swell('more'):
            if u[key]:
                for k in u[key].split('\n'):
                    left.add(k.strip())
        if key == 'fest':
            return sorted(left, key=lambda x: x[-4:] if x[-4].isdigit() else f'0{100000-ord(x[0])}', reverse=True)
        elif key == 'invite':
            return sorted(left, key=lambda x: x if x[0].isdigit() else f'0{100000-ord(x[0])}', reverse=True)
        else:
            return sorted(left)

    def getView(self, dcUK):
        top = dcUK.upList.partition('|')[2]  # training|fest|invite
        left = dcUK.selected
        mainDocs = []

        for dc in swell('more'):
            if not (dc[top] and left in dc[top]):
                continue

            title = _div(f'{dc.FULL_NAME}\n{dc.phone}',
                className='mCell', s2=1, br=1, **style(width='100%', letterSpacing=1))

            btnPay = _btnD('Р', 'cmdNewPay', dc.id, className=f'btnIcon mBtn fv2 fv2yes', title='оплачено')
            btnE = _btnEdit('cmdEdit', dc.id)
            btnD = _btnDel('cmdDel', f'mainList|{dc.id}|nv_Profile')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto'),
                children=[title, btnPay, btnE, btnD])
            mainDocs.append([dc.id, row, dc.FULL_NAME])

        mainDocs = [ [m[0], m[1]] for m in sorted(mainDocs, key=lambda x: x[2])]
        return {'mainDocs': mainDocs, 'refsDocs': None}

    # *** *** ***

