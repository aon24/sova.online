# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import swell
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field, _span
from arm.tools.loadWell import loadLanding

# *** *** ***

WIDTH = 1200
'''
*** Landing-forms ***
форма "Отзывы" для сайта
'''


class a_feedback(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Отзывы'
        self.dbAlias = 'draft'
        super().__init__(request)

    # ***

    def page(self, request):
        if self.mode in ['edit', 'new']:
            prj = [
                _div(**style(textAlign='right'), children=[
                    _span('Проект ', className='label', **style(display='inline-block')),
                    _field('project', **style(display='inline-block', textAlign='left', width=150)),
                ]),
                _div(**style(textAlign='right'), children=[
                    _span('Имя страницы ', className='label', **style(display='inline-block')),
                    _field('pageName', **style(display='inline-block', textAlign='left', width=150)),
                ]),
                _div(**style(textAlign='right'), children=[
                    _span('key ', className='label', **style(display='inline-block')),
                    _field('key', 'lbsd', swell('3dKeys'), **style(display='inline-block', textAlign='left', width=150))
                ]),
            ]
        else:
            prj = []

        main = _div(**style(height='100%', overflow='auto'), children=[
            *prj,
            self.materials(tmpl=True),
        ])
        return self.docPage([main])

    # ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        dcUK.doc.key = dcUK.doc.key or dcUK.key
        dcUK.doc.project = dcUK.doc.project or dcUK.project
        dcUK.doc.rainbow = dcUK.doc.rainbow or '\n'.join(['#ff0000ff', '#ffa500ff', '#ffff00ff', '#008000ff', '#0000ffff', '#4b0082ff', '#ee82eeff'])

    # *** *** ***

    def querySave(self, dcUK):
        return True

    # *** *** ***

    def afterSave(self, dcUK):
        loadLanding()
        return True

    # *** *** ***
