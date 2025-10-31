# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field
from arm.tools.loadWell import loadLanding
from arm.api.forms.a_design.fields import getField

# *** *** ***

WIDTH = 1200
'''
форма "О платформе" для сайта
'''


class about(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js',
                         f'/api/jsv?forms/{self.form}/turnOn.js',
                         f'/api/jsv?forms/{self.form}/about_read.js']
        self.title = 'О платформе'
        self.dbAlias = 'draft'

        self.edges = dict(
            face={'tuning': {'boxContent': 3,
                             'fieldType': 'json',
                             'xName': 'cube_left',
                             'minWidth': '100%'}},
            left={'tuning': dict(bgStyle='color', backgroundColor='#f00')},
            right={'tuning': dict(bgStyle='color', backgroundColor='#0f0')},
            top={'tuning': dict(bgStyle='color', backgroundColor='#00f')},
            far={'tuning': dict(bgStyle='color', backgroundColor='#000')},
        )
        super().__init__(request)

    # ***

    def page(self, request):
        sova = _div(**style(textAlign='center'), children=[
            # _div(name='scale', children=[
            #     scale,
            #     _btnD('\xa0запомнить\xa0', 'save_etc', className='redRedBut', **style(display='inline-block')),
            # ]),
            # _h3('Платформа Sova.online'),
            # _field('pdf', 'fileShow', 'short'),
            # _fileShow('fm', label='файлы'),
            # _a('ЛК студента.pdf'), _br(),  # href='/static/doc/ЛК студента.pdf'),
            # _a('ЛК куратора.pdf'), _br(),  # href='/static/doc/ЛК студента.pdf'),
            # _a('ЛК преподавателя.pdf'), _br(),  # href='/static/doc/ЛК студента.pdf'),
            # _a('офис.pdf'),  # href='/static/doc/ЛК студента.pdf'),
            _div(
                children=[_field('cube', 'cube', readOnly=1, xyz=[600, 300, 'x'], perspective=700, edges=self.edges)]
            ),
        ])
        return self.docPage([sova])

    # ***

    def queryOpen(self, request):
        dcUK = request.dcUK
        doc = dcUK.doc
        if 1:
            doc.cube_left = getField('login2d_fd', request)

        doc.key = doc.key or dcUK.key
        doc.project = doc.project or dcUK.project
        doc.rainbow = doc.rainbow or '\n'.join(['#ff0000ff', '#ffa500ff', '#ffff00ff', '#008000ff', '#0000ffff', '#4b0082ff', '#ee82eeff'])

    # *** *** ***

    def querySave(self, dcUK):
        return True

    # *** *** ***

    def afterSave(self, dcUK):
        loadLanding()
        return True

    # *** *** ***
