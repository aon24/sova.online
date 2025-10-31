# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _tabNew, _field
from arm.api.forms.SessionTmpl.SessionTmpl import queryOpenForGrSt

# *** *** ***


class SessionGr(Page):
    '''
    Сессия группы. Документ в БД. Таблица nv_SessionGr
    SessionTmpl-SessionGr-SessionSt - три основные формы в ЛК
    1. SessionTmpl - шаблон по которому создаются сессии групп и студентов.
        содержит видео и другие материалы по конкретной сессии(лекции)
    2. SessionGr - отображает(не хронит в себе) то, что есть в SessionTmpl,
        хранит в себе привязку к шаблону и к группе и дату-время
    3. SessionSt - отображает(не хронит в себе) то, что есть в SessionTmpl и в SessionGr,
        хранит в себе привязку к сессии группы и к студенту, ответы на задания, обратную связь конкретного студня
    '''
    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Сессия группы'
        self.dbAlias = 'nv_SessionGr'

        super().__init__(request)

    # ***

    def page(self, request):
        main = _div(**style(height='100%', overflow='auto'), children=[
            _div('Видеоматериалы', className='h2', name='video'),
            _field('videoGrid', 'grid'),
            self.materials(),
        ])

        # ***

        table = [
            ('/image/i.png', self.common(gr=True), 50, 'информация'),
            ('/image/s_ummv.png', main, 50, 'учебные материалы'),
            ('/image/s_dz.png', self.jobs(gr=True), 50, 'задания'),
            ]

        return self.docPage([_tabNew('SST_Table_FD', tabs=table)])

    # ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        self.title = dcUK.title or 'Сессия группы'

        doc = dcUK.doc
        if dcUK.mode == 'new':
            if not (dcUK.tmplId and dcUK.nvgroup):
                raise Exception(f'{self.form}: dcUK.tmplId or dcUK.nvgroup is null')
            doc.sessionTmpl = dcUK.tmplId
            doc.nvgroup = dcUK.nvgroup
            doc.date_begin = dcUK.date_begin
            doc.status = 'active'

        grOGr = well('groups_groupId', doc.other_group)
        if grOGr:
            doc.other_group_fd = grOGr.title

        gr = well('groups_groupId', doc.nvgroup)
        if gr:
            doc.group_fd = gr.title
            doc.commonGroups = gr.commonGroups
            if not doc.curator:
                doc.curator = gr.curator

        queryOpenForGrSt(doc)

    # *** *** ***
