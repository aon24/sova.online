# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well, DC
from arm.tools.loadWell import loadWell
from arm.api.forms.classPage import Page
from arm.tools.dbToolkit.DJ import docFromDB
from arm.api.forms.formTools import style,_div,_tab,_field

import json

# *** *** ***

WIDTH = 1200


class SessionSt(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Сессия студента'
        self.dbAlias = 'nv_SessionSt'

        super().__init__(request)

    # ***

    def page(self, request):
        main = _div(**style(height='100%', overflow='auto'), children=[
            _div('Видеоматериалы', className='h2'),
            _field('videoGrid', 'grid'),
        ])

        # ***

        # ***
        con = _div()

        fields = []
        for i, s in enumerate(well('ratings') or []):
            fields += [_div(s, className='h4') , _field(f'assLec{i+1}', 'rating', **style(margin='auto'))]

        ass = _div(**style(padding=10, height='100%', overflowY='auto'),
                name='ass',
                children=[
                    _div('Оцените', className='h2'),
                    *fields,
                    self.btnSaveClose
                ]
            )

        table = [
            ('1️⃣', self.common(st=True), 45),  # 🦉📓
            ('Видео', main, 70),
            ('Материалы', self.materials(st=True), 100),
            ('Практика', con, 90),
            ('Оценить', ass, 90, 'ass'),
        ]

        return self.docPage([_tab(width=110, tabs=table, ah=6)])

    # ***

    def queryOpen(self, dcUK):
        doc = dcUK.doc
        full_name = well('profiles', doc.pref).full_name

        if not (full_name == dcUK.fullName or dcUK.q_superUser):
            doc.noAss_fd = 1
            for k in list(doc.keys()):
                if k.startswith('ASSLEC'):
                    del doc._KV_[k]

        dc = DC(dbAlias='nv_SessionGr', unid=doc.sessionGr)
        docFromDB(dc)
        docGR = dc.doc

        dc.dbAlias = 'nv_SessionTmpl'
        dc.unid = docGR.sessionTmpl
        docFromDB(dc)
        docTm = dc.doc

        if 'куратор' not in dcUK._role and not dcUK._staff:
            doc.student_FD = 1
            dcUK.fd = 'STATUS'

        doc.duration = docGR.duration
        doc.fullName = full_name

        doc.date_begin = docGR.date_begin
        doc.date_end = docGR.date_end
        doc.curator = docGR.curator
        doc.lector = docGR.lector
        doc.status = docGR.status
        # doc.semester = docGR.semester

        doc.group_fd = well('groups_groupId', docGR.nvgroup).title
        doc.nvgroup_fd = f'{doc.group_fd}|{docGR.nvgroup}'
        other = well('groups_groupId', doc.other_group)
        doc.other_group_fd = other and other.title

        # ***

        doc.title = docTm.title
        doc.nvEvent = docTm.nvEvent
        doc.partLabel = docTm.partLabel
        doc.description = docTm.description

        doc.videoList = docTm.videoList
        if doc.videoList and doc.videoList[0] != '[':
            doc.videoList = json.dumps([{'url': it} for it in doc.videoList.split('\n') if it], ensure_ascii=False)

        doc.fm = docTm.fm
        doc.mtx = docTm.mtx
        doc.ref = docTm.ref
        doc.rtf = docTm.rtf
        doc.colorStyleMap = docTm.colorStyleMap

        if doc.owner:
            doc.other_fd = doc.group_fd
            doc.owner_fd = well('groups_groupId', doc.owner).title

        # *** *** ***
    def querySave(self, dcUK):
        pref = dcUK.doc.pref
        sgr = well('sessionGr_Id', dcUK.doc.sessionGr_Id)
        stm = sgr and sgr.sessionTmpl_id
        if not dcUK.doc.other_group:  # проверить, нет ли для этого студня такой сессии в др.гр.
            for k, arr in well('other').items():  # k = f'{dc.other_group}|{stm}'
                ogr, _, tmpl = k.split('|')
                if tmpl == stm and pref in arr:
                    arr.remove(pref)
                    loadWell('SessionSt', ogr)

        return True

