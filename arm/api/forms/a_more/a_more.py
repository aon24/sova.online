# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import swell
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field, _span, _btnD
from arm.tools.loadWell import loadLanding
from arm.tools.first import snd
from arm.tools.common import today
from arm.api.forms.etc.etc import scale

from django.http import HttpResponse

# *** *** ***

WIDTH = 1200
'''
*** Landing-forms ***
форма для сайта, аналогична вкладке materials из форм Session*,
но с полями для сайтовых страниц: project, pageName, key
'''


class a_more(Page):
    noCaching = True

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Материалы'
        self.dbAlias = 'draft'
        super().__init__(request)

    # ***

    def getData(self, dcUK):
        if dcUK.cmd == 'addFeedback':
            snd(f'\n<<C+{today()}>\n{dcUK.buf}\n<<B+{dcUK.fullName}>\n_________________\n', cat='addFeedback')
            return HttpResponse('OK')

        return HttpResponse('', status=400)

    # ***
    def page(self, request):
        if self.mode in ['new', 'edit']:
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
            size = None
            materials = self.materials(tmpl=True)
        else:
            prj = []
            size = _div(name='scale', **style(textAlign='center'), children=[
                scale,
                _btnD('\xa0запомнить\xa0', 'save_etc', className='redRedBut', **style(display='inline-block')),
                _div(className='setting-line'),
            ])
            materials = self.materials()

        main = _div(**style(overflow='auto'), children=[
            *prj,
            size,
            materials,
        ])
        # if request.dcUK.mode != 'edit' and request.dcUK.doc.pageName == 'feedback':
        #     addFB = _btnD('ДОБАВИТЬ ОТЗЫВ', 'addFeedback', className='toolbar-button')
        #     tool = [addFB, toolbar.close_]
        # else:
        #     tool = None

        return self.docPage([main, _field('videoGrid', 'grid'), ])

    # ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        doc = dcUK.doc
        doc.key = doc.key or dcUK.key
        doc.project = doc.project or dcUK.project
        doc.videoList = doc.videoList or '[]'
        doc.rainbow = doc.rainbow or '\n'.join(['#ff0000ff', '#ffa500ff', '#ffff00ff', '#008000ff', '#0000ffff', '#4b0082ff', '#ee82eeff'])

    # *** *** ***

    def querySave(self, dcUK):
        return True

    # *** *** ***

    def afterSave(self, dcUK):
        loadLanding()
        return True

    # *** *** ***
