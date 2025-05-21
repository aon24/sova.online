# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import DC, swell
from arm.tools.first import err

from ..formTools import _fileShow, labField, gridStyle, style, _div, _h2, _field, labeldc, labell
from ..classPage import Page
from arm.tools.dbToolkit.DJ import docFromDB

# *** *** ***


class NVGroup(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Группа'
        self.dbAlias = 'nv_NVGroup'

        super().__init__(request)

    # ***

    def page(self, request):
        fields = [
            labeldc('ПРОГРАММА'),
            _div(**style(textAlign='center',font='bold 15px Arial',color='#036'),children=[
                _field('programm','fd')
            ]),
            _h2('Группа',**style(textAlign='center',margin=0,letterSpacing=2)),

            *labField('Номер (сначала год, затем №)', 'title', 'tx'),

            _div(**gridStyle('1fr 10px 1fr', width=260, margin='auto'), children=[
                    labeldc('Начало занятий'), _div(), labeldc('Окончание'),
                    _field('date_begin', 'dt'), _div(), _field('date_end', 'dt'),
                ]
            ),

            _div(children=[
                    labell('Куратор', name='curator'),
                    _field('curator', 'lbsd', '/api/well?clues=куратор2', name='curator'),
                    labeldc('В расписании группу видят'),
                    _field('commonGroups', 'lbsd', '/api/well?clues=groupsCat', alias=1, **style(margin='auto', width=250)),
                ],
                **style(border='2px solid #fff', margin=5, padding=5, background='#e0F0ff50'),
            ),

            *labField('Описание', 'description', 'tx'),

            _fileShow('FILES1_', wl='40mm', label='вложения '),

            self.noteStatus(),
        ]

        return self.docPage(fields)

    # ***

    def queryOpen(self, r):
        doc = r.dcUK.doc
        doc.status = doc.status or 'active'
        doc.programm = doc.programm or swell('programm')[0]

    def afterSave(self, dcUK, pk):  # by created new doc dcUK.doc.pk is None
        if dcUK.doc.curator and dcUK.doc.title and pk:
            newGr = dcUK.doc.title
            try:
                pref = dcUK.doc.curator.partition('|')[2]
                dc = DC(dbAlias='nv_Profile', unid=pref)
                if not docFromDB(dc):
                    err(f'NVGroup. Profile get err for pk={pref}', cat='afterSave')
                    return

                oldGr = dc.doc.curator_groups
                if oldGr:
                    ls = []  # при изменении названия группы чтобы у куратора в профайле не дублировались
                    for gr in oldGr.split('\n'):
                        grId = gr.partition('|')[2]
                        if grId and grId != pk:
                            ls.append(gr)
                    ls.append(f'{newGr}|{pk}')
                    dc.doc.curator_groups = '\n'.join(ls)
                else:
                    dc.doc.curator_groups = f'{newGr}|{pk}'

                if oldGr != dc.doc.curator_groups:
                    dc.save()

            except:
                err(f'NVGroup. Profile get err for pk={pk}', cat='querySave')
                return

        return True

    # ***

