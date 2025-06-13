# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import swell, config, well
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field, _span, labField
from arm.tools.loadWell import loadLanding
from arm.api.forms.toolbars import toolbar

# *** *** ***

WIDTH = 1200
"""
форма для генерации html
генерит страницу в doc.html_FD из поля body с подстановкой 4-х шаблонов
def queryOpen(self, r):
    ...
    doc.html_FD = f'{doc.body.replace(*tr(1)).replace(*tr(2)).replace(*tr(3)).replace(*tr(4))}'
"""


class a_html(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = config.orgName
        self.dbAlias = 'draft'
        self.css = ''
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

                *labField('jsCss', 'jsCss'),
                *labField('title', 'title'),
                *labField('templ_1', 'templ_1'),
                *labField('templ_2', 'templ_2'),
                *labField('templ_3', 'templ_3'),
                *labField('templ_4', 'templ_4'),
                *labField('body', 'body'),

            ]
            return _div(className='bg52', children=[
                _div(className='toolbar', children=[toolbar.saveClose, toolbar.close_]),
                _div(className='page', children=prj),
            ])
        else:
            prj = [_div(**style(width='100%', height='100%'), children=[_field('html_FD', 'html')])]
            return _div(className='bg52', children=[
                _div(className='page', children=prj),
                _div(children=[toolbar.close_],
                    ** style(display='flex', justifyContent='center', height=40, maxHeight=40,
                            padding=3)),
            ])


    # ***

    def getJsCssUrl(self, request):
        if request.dcUK.mode in ['read', 'preview']:
            return self.jsCssUrlRead + self.css
        else:
            return self.jsCssUrlEdit

    # ***
    def queryOpen(self, r):

        def tr(nt):
            ls = doc[f'templ_{nt}'].split('\n')
            return ls[0], '\n'.join(ls[1:])

        dcUK = r.dcUK
        doc = dcUK.doc
        self.css = doc.jsCss.split('\n')
        doc.html_FD = f'{doc.body.replace(*tr(1)).replace(*tr(2)).replace(*tr(3)).replace(*tr(4))}'
        doc.key = doc.key or dcUK.key
        doc.project = doc.project or dcUK.project

        if dcUK.mode == 'new':
            if dcUK.sourceDoc:
                for ldc in well('landing'):
                    if ldc.unid == dcUK.sourceDoc:
                        for k, v in ldc.items():
                            if k not in ['UNID', 'CREATED' , 'CREATOR' , 'MODIFIED', 'MODIFIER', 'REF']:
                                doc[k] = v

    # *** *** ***

    def querySave(self, dcUK):
        return True

    # *** *** ***

    def afterSave(self, dcUK):
        loadLanding()
        return True

    # *** *** ***
