# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
<svg width="100000" height="100000">
    <defs>
        <path id="myTextPath2" d="M40, 200 a 30,30 0 0 1 300,0"/>
     </defs>
    <text x="10" y="10" style={{stroke: '#036', font: 'normal 30px Times'}}>
        <textPath xlinkHref="#myTextPath2">
            look into the future
        </textPath>
    </text>
</svg>
'''
from .a_screens import blankScreens
from .fields import getField
from arm.tools.first import err
from arm.tools.dbToolkit.Book import histFromDB
from arm.tools.loadWell import loadLanding
from arm.settings import BASE_DIR

from arm.api.forms.sno import snoDB
from arm.api.forms.formTools import style, _div, _field
from arm.api.forms.toolbars import toolbar
from arm.api.forms.classPage import Page

import json
import os
import zlib

# *** *** ***


class a_design(Page):

    def __init__(self, request):
        self.title = 'html-edit'
        self.form = 'a_design'
        s = f'/api/jsv?forms/{self.form}'
        self.jsCssUrlEdit = [f'{s}/{self.form}.js', f'{s}/turnOn.js']
        self.jsCssUrlRead = [f'{s}/a_design_read.js', f'{s}/turnOn.js']
        self.dbAlias = 'draft'
        self.styles = '<link href="/static/fonts/home.css" rel="stylesheet">\n'
        # self.styles = '<link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">\n'

        super().__init__(request)

    # *** *** ***

    def page(self, request):
        mode = request.dcUK.mode
        hPage = 'calc(100vh - 50px)'
        if mode == 'preview':
            return _div(
                **style(overflow='hidden', height='100%'),
                children=[
                    toolbar.info(mode),
                    _div(**style(height=hPage, overflow='auto'),
                        children=[_field('root', 'box', **style(margin='auto', height=hPage))]),
                ]
            )
        elif mode == 'read':
            return _div(
                **style(overflowY='auto', overflowX='hidden', minHeight='100%'),
                children=[
                    _field('root', 'box', **style(margin='auto', height='100%'))
            ])

        return _div(
            className='bg52',
            **style(position='relative', overflow='hidden'),
            children=[
                toolbar.design(mode),
                _div(**style(height=hPage, overflow='auto', marginTop=50),
                    children=[_field('root', 'box', **style(margin='auto', height=hPage))]),
            ]
        )

    # *** *** ***

    def queryOpen(self, request):
        dcUK = request.dcUK
        doc = dcUK.doc
        self.title = doc.title or doc.pageName or 'html-edit'

        # doc.root = doc.root.replace('http://result-systems.online', 'https://result-systems.ru')
        # doc.webSocketServer_FD = f'{config.ws_server}:{config.ws_port}'
        doc.created_FD = doc.DT('created')
        doc.modified_FD = doc.DT('modified')
        doc.published_FD = doc.published
        doc.creator_FD = doc.creator
        doc.modifier_FD = doc.modifier
        doc._syles_ = ''
        doc.docNo_FD = f"№ {doc.pref}{doc.docNo}{doc.suff} от {doc.D('created')}"

        doc.dir = doc.dir or '0'
        doc.root = doc.root or blankScreens(dcUK.key)
        doc.rainbow = doc.rainbow or '\n'.join(['#ff0000ff', '#ffa500ff', '#ffff00ff', '#008000ff', '#0000ffff', '#4b0082ff', '#ee82eeff'])
        doc.project = doc.project or dcUK.project
        doc.key = doc.key or dcUK.key
        if doc.key == 'все':
            doc.key = '2d'

        if doc.theScript:
            path = os.path.join(BASE_DIR, 'DB', 'scripts', dcUK.fullName.partition(' ')[0] or 'guest')
            try:
                # with open(os.path.join(path, 'f4292d475fa7423196a0ebdb8a225c9d'), 'br') as f:
                with open(os.path.join(path, dcUK.unid), 'br') as f:
                    s = f.read()
                    doc.theScript = zlib.decompress(s).decode()
            except Exception as ex:
                err(f'the load script error: {ex}', cat='a_design')

        if doc.pageName == 'login2d':
            doc.login2d_fd = getField('login2d_fd', request)

# *** *** ***

    def querySave(self, dcUK):
        if dcUK.doc.docNo:
            return True

        n = snoDB(dcUK)
        if n:
            dcUK.doc.docNo = n
            return True

# *** *** ***

    def afterSave(self, dcUK):
        loadLanding()
        return True

# *** *** ***

    def getData(self, dcUK):
        return histFromDB(dcUK)

# *** *** ***


def delNecessary(dcUK):

    def oneBox(box, r2b):
        for k, v in box.items():
            if k in ['boxes', 'cells']:
                r2b[k] = []
                for it in v:
                    bc = {}
                    oneBox(it, bc)
                    r2b[k].append(bc)

            elif k == 'tuning':
                r2b[k] = {}
                for k1, v1 in v.items():
                    if v1:
                        r2b[k][k1] = v1
            elif k == 'content' and not v[0] and not v[1]:
                pass
            else:
                r2b[k] = v

    try:
        root = json.loads(dcUK.doc.root)
        r2 = {}
        oneBox(root, r2)
        dcUK.doc.root = json.dumps(r2, ensure_ascii=False)
    except Exception as ex:
        err(ex, cat='a_design.querySave.delete necessary')
