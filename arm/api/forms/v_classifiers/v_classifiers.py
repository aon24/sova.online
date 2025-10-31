# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well, swell
from arm.api.forms.formTools import style,_div,_search,_field,_btnDel,_btnEdit,_btnNew
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class v_classifiers(Page):
    '''
    CRM вид справочники
    '''
    title = 'Справочники'
    dbAlias = 'nv_Classifier'
    leftList = None
    noCaching = True
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']

        super().__init__(request)

    def getData(self, dcUK):
        data = self.getView(dcUK) if dcUK.cmd == 'getSelected' else f'invalid cmd: {dcUK.cmd}'
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def page(self, request):
        status = ['актив', 'архив', 'все']
        category = set()
        [category.add(dc.category) for dc in swell('classifiers') if dc.category]
        category = sorted(category)
        category.append('все')

        self.upField = _div(children=[
            _div(className='toolbar',children=[toolbar.close_]),
            _field('status', 'band', status, recalcText=1, **style(margin='auto', display='table', width='auto')),
            _field('category', 'band', category, recalcText=1, **style(margin='auto', display='table', width='auto'))
        ])

        self.viewbar = self.makeViewbar(
            leftBtn=[_btnNew(self.dbAlias)],
            rightBtn=_search()
        )

        return self.shamrock(addUrl='&status={status}&category={category}')

    # *** *** ***

    def getView(self, dcUK):
        status = dcUK.status
        category = dcUK.category
        mainDocs = []

        for cls in sorted(swell('classifiers'), key=lambda dc: dc.description.lower()):
            pk = cls.id

            if status != 'все':
                if status == 'актив' and cls.status != 'active':
                    continue
                if status == 'архив' and cls.status != 'closed':
                    continue

            if category != 'все'and category != cls.category:
                continue

            lst = cls.list.replace('\n', '-')
            tit = cls.title.replace('\n', '-')
            title = _div(f"{cls.description} -- {tit}\n{lst or cls.formula}",
                className='mCell', s2=1, br=1, **style(width='100%', paddingLeft=2, letterSpacing=1))

            pk = str(pk)
            btnE = _btnEdit('cmdEdit', pk)
            btnD = _btnDel('cmdDel', f'mainList|{pk}|nv_Classifier')  # удалить док из вида mainList

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                children=[title, btnE, btnD])
            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}


# *** *** ***
