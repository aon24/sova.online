# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import swell

from ..formTools import labField, style, _div, _h2, _field
from ..classPage import Page

# *** *** ***


class Classifier(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Справочник'
        self.dbAlias = 'nv_Classifier'

        super().__init__(request)

    # ***

    def page(self, request):
        cat = set()
        [cat.add(dc.category) for dc in swell('classifiers') if dc.category]

        status = _div(**style(marginTop=10, display='grid', gridTemplateColumns='1fr 60px 120px'), children=[
                     _div(), _div('Статус', className='label'),
                     _field('status', 'lbsd', self.status, placeholder='выбирай', alias=1)
        ])

        fields = [
            _h2('Справочник', **style(textAlign='center', margin=0, letterSpacing=2)),

            *labField('Название', 'description', 'tx'),
            *labField('Категория', 'category', 'lbse', sorted(cat)),
            *labField('Список', 'list', 'tx', **style(font='normal 16px Courier')),
            *labField('Формула (Python)', 'formula', 'tx', **style(font='normal 16px Courier')),
            *labField('Имя в системе', 'title', 'tx'),

            *labField('Комментарий', 'notes', 'tx'),

            status,
            _div(**style(height=10))
        ]

        return self.docPage(fields)

    # ***

    def queryOpen(self, r):
        r.dcUK.doc.status = r.dcUK.doc.status or 'active'

    def querySave(self, dcUK):
        return True

    # ***
