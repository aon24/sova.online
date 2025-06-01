# -*- coding: utf-8 -*-
'''
AON 2022

'''
from arm.api.forms.formTools import style, _div, _btnD, _img, _input, _field, labell
from arm.api.forms.classPage import Page
from arm.tools.imgHeader import what
from arm.tools.first import err
from arm.api.forms.toolbars import toolbar
from arm.settings import BASE_DIR
from arm.tools.httpMisc import nvResponse

import os

# *** *** ***


class img(Page):
    title = 'Pictures'
    noCaching = True
    dbAlias = 'arm'
    form = 'img'

    def __init__(self, request):
        self.jsCssUrl = '/api/jsv?forms/img/img.js'
        self.pictures = self.pic = os.path.join('static', 'pictures')
        self.formDir = ''
        super().__init__(request)

    # *** *** ***

    def getData(self, dcUK):
        if dcUK.cmd == 'getFormDir':
            return nvResponse(self.formDir)
        else:
            return nvResponse(f'Server error. cmd: {dcUK.cmd}', status=400)
    # *** *** ***

    def page(self, request):
        if request.dcUK.formDir:
            self.formDir = request.dcUK.formDir
            self.pictures = os.path.join(self.pic, self.formDir)
        body = _div(children=[
            *self.picList(request),
            _input(type="file", id='inputBgFiles', onChange='addFiles', multiple=False, **style(display='none'))
        ])
        btnFiles = _btnD('Выбрать и загрузить файл', 'btnFiles', title='Выбрать файл', className='toolbar-button')
        btnList = _field('btnList', 'chb', ['Список'])
        # btnList = _btnD('Список', 'btnList', className='toolbar-button')

        return self.docPage([body], tool=[btnFiles, btnList, toolbar.close_])

    # *** *** ***

    def picList(self, request):  # AnyDesk
        subDir = request.dcUK.subDir
        try:
            path = os.path.join(BASE_DIR, self.pictures, subDir)
            lsfiles = os.listdir(path)
        except Exception:
            try:
                subDir = ''
                path = os.path.join(BASE_DIR, self.pictures)
                lsfiles = os.listdir(path)
            except Exception as ex:
                s = f'404 pages.img: os.listdir-error({path}): {ex}'
                err(s, cat='pages.img')
                return [_div(s)]

        ls = []
        btn = []
        if subDir:
            p = os.path.split(subDir)[0]
            btn.append(
                _btnD('⇑', 'chDir', p, className='chDir', title='вернуться', children=[
                    _div('⇑ ⇑', **style(padding=2)),
                    _div('⇑ ⇑ ⇑', **style(padding=3)),
                    _div('вернуться'),
                ])
            )
            subDir += os.sep

        for k in sorted(lsfiles):
            fil = os.path.join(path, k)
            if os.path.isfile(fil) and what(fil):
                if request.dcUK.list == '1':
                    item = _btnD('', 'oneImg', f'/{self.pictures}/{subDir}{k}', className='chDir',
                        title=f'Выбрать файл "{k}"',
                        **style(margin=5, display='flex'),
                         children=[
                            labell(k, **style(width=200)),
                            _img(src=f'/{self.pictures}/{subDir}{k}', alt=k, **style(width=100, height=100))
                        ],)
                else:
                    item = _btnD('', 'oneImg', f'/{self.pictures}/{subDir}{k}', className='chDir',
                        title=f'Выбрать файл "{k}"',
                        **style(margin=5),
                        children=[
                            _img(src=f'/{self.pictures}/{subDir}{k}', alt=k, **style(width=200, height=200))
                        ],
                    )
                ls.append(item)
            elif os.path.isdir(fil):
                btn.append(
                    _btnD('', 'chDir', f'{subDir}{k}', className='chDir', title='открыть',
                        children=[
                            _img(src=f'/image/folder.png'),
                            _div(k, **style(padding='0 10px'))
                    ])
                )
        if btn:
            ls = [_div(children=btn, **style(textAlign='center', margin=5))] + \
                 [_div(children=ls, **style(textAlign='center', margin=0))]
        return ls

    # *** *** ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        dcUK.doc.vl = dcUK.vl  # index of videoList
        dcUK.doc.subDir = dcUK.subDir
        dcUK.doc.btnlist = 1 if dcUK.list == '1' else ''

    # *** *** ***

