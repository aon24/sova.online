# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.DC import well, swell
from arm.tools.loadWell import loadWell
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field, _tabNew
from arm.api.forms.SessionTmpl.SessionTmpl import queryOpenForGrSt
from arm.api.forms.toolbars import toolbar

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
            _div('Видеоматериалы', className='h2', name='video'),
            _field('videoGrid', 'grid'),
            self.materials(),
        ])

        # ***

        # ***

        fields = []
        for i, s in enumerate(swell('ratings') or []):
            fields += [_div(s, className='h4') , _field(f'assLec{i+1}', 'rating', **style(margin='auto'))]

        tass = [toolbar.saveClose, toolbar.close_] if self.mode == 'edit' else [toolbar.close_]
        ass = _div(**style(padding=10, height='100%', overflowY='auto'),
                name='ass',
                children=[
                    _div('Оцените', className='h2'),
                    *fields,
                    _div(**style(textAlign='center', paddingTop=4), children=tass)
                ]
            )
        if self.noicons:
            table = [
                # ('1️⃣', self.common(st=True), 45, 'информация'),  # 🦉📓
                # ('Материалы', main, 100, 'учебные материалы'),
                # ('Задания', self.jobs(st=True), 80, 'задания'),
                # ('Обр. связь', ass, 100, 'Обратная связь'),
                ('Материалы', main, 100, 'учебные материалы'),
                ('Обр. связь', ass, 100, 'Обратная связь'),
                ('1️⃣', self.common(st=True), 45, 'информация'),  # 🦉📓

            ]
        else:
            table = [
                # ('/image/i.png', self.common(st=True), 50, 'информация'),
                # ('/image/s_ummv.png', main, 50, 'учебные материалы'),
                # ('/image/s_dz.png', self.jobs(st=True), 50, 'задания'),
                # ('/image/s_feedback.png', ass, 50, 'Обратная связь'),
                ('/image/s_ummv.png', main, 50, 'учебные материалы'),
                ('/image/s_feedback.png', ass, 50, 'Обратная связь'),
                ('/image/i.png', self.common(st=True), 50, 'информация'),
            ]

        tool = [toolbar.saveClose, toolbar.close_] if self._role == 'куратор' or self._staff else [toolbar.close_]
        return self.docPage([_tabNew('sst_Table_FD', tabs=table)], tool)

    # ***

    # костыль, чтобы никто не видел поля с оценкой, если есть noAss_fd
    def getOldValue(self, r, fv, do):
        return {k: do.get(k, '') for k in fv if do.get(k, '') != fv[k] and not (fv.get('NOASS_FD') and k.startswith('ASSLEC'))}

    def queryOpen(self, r):
        dcUK = r.dcUK
        doc = dcUK.doc
        full_name = well('profiles', doc.pref).full_name
        doc.fullName = full_name

        if not (full_name == dcUK.fullName or dcUK._superUser):
            doc.noAss_fd = 1
            for k in list(doc.keys()):
                if k.startswith('ASSLEC'):
                    del doc._KV_[k]

        if 'куратор' not in dcUK._role and not dcUK._staff:
            doc.student_FD = 1
            dcUK.fd = 'STATUS'


        other = well('groups_groupId', doc.other_group)
        doc.other_group_fd = other and other.title

        # ***

        if doc.owner:
            doc.other_fd = doc.group_fd
            doc.owner_fd = well('groups_groupId', doc.owner).title

        queryOpenForGrSt(doc, student=True)

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

