# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well, DC
from arm.api.forms.classPage import Page
from arm.tools.dbToolkit.DJ import docFromDB
from arm.api.forms.formTools import style,_div,_tab,_field,labField

import json

# *** *** ***

class SessionGr(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Сессия группы'
        self.dbAlias = 'nv_SessionGr'

        super().__init__(request)

    # ***

    def page(self, request):
        main = _div(**style(height='100%', overflow='auto'), children=[
            _div('Видеоматериалы', className='h2'),
            _field('videoGrid', 'grid'),
        ])

        # ***

        con = _div()

        table = [
            ('1️⃣', self.common(gr=True), 50),  # 🦉📓
            ('Видео', main, 80),
            ('Материалы', self.materials(gr=True), 90),
            ('Практика', con, 90),
        ]

        return  self.docPage([_tab(width=110, tabs=table, ah=6)])

    # ***

    def queryOpen(self, dcUK):
        self.title = dcUK.title or 'Сессия группы'

        doc = dcUK.doc
        if dcUK.mode == 'new':
            if not (dcUK.tmplId and dcUK.nvgroup):
                raise Exception(f'{self.form}: dcUK.tmplId or dcUK.nvgroup is null')
            doc.sessionTmpl = dcUK.tmplId
            doc.nvgroup = dcUK.nvgroup
            doc.date_begin = dcUK.date_begin
            doc.status = 'active'

        dc = DC(dbAlias='nv_SessionTmpl')  # bag: unid=doc.sessionTmp)
        dc.unid = doc.sessionTmpl
        docFromDB(dc)
        docTm = dc.doc

        # doc.title = doc.title or docTm.title
        doc.lector = doc.lector or docTm.lector

        v2 = None  # doc.videoListAdd
        if v2:
            doc.videoList_fd += f'\n{v2}'

        gr = well('groups_groupId', doc.nvgroup)
        doc.group_fd = gr.title
        doc.commonGroups = gr.commonGroups
        grOGr = well('groups_groupId', doc.other_group)
        if grOGr:
            doc.other_group_fd = grOGr.title

        doc.partLabel = docTm.partLabel
        doc.description = docTm.description
        doc.nvEvent = docTm.nvEvent

        doc.fm = docTm.fm
        doc.mtx = docTm.mtx
        doc.ref = docTm.ref
        doc.rtf = docTm.rtf
        doc.colorStyleMap = docTm.colorStyleMap

        doc.videoList = docTm.videoList
        if doc.videoList and doc.videoList[0] != '[':
            doc.videoList = json.dumps([{'url': it} for it in doc.videoList.split('\n') if it], ensure_ascii=False)

        if not doc.curator:
            doc.curator = gr and gr.curator

        doc.openTmpl = f"{docTm.title}|previewNew|title={docTm.title}&form=SessionTmpl&unid={doc.sessionTmpl}&dbAlias=nv_SessionTmpl&rsMode=edit"

    # *** *** ***

