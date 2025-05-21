# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
'''
from arm.tools.DC import well
from arm.api.forms.formTools import  _div, _field, style
from arm.api.forms.v_lk_curator.v_lk_curator import v_lk_curator
from arm.api.forms.toolbars import toolbar

# *** *** ***

class v_lk_curator2(v_lk_curator):
    '''
    вызывается при нажатии машкой на эскиз или квадратик в календарe (в ARM или в v_shedule cmd: dayX)
    открывает список студентов для заданной сессии
    Установка/сброс "Д-З-Р-V" для выделенных студней
    Отличие от v_lk_curator: нет списка слева, т.к. смотрим студней для конкретной сессии
    '''
    def __init__(self, request):
        super().__init__(request)
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.leftWidth = 0
        self.leftList = None

    # *** *** ***

    def page(self, request):
        self.upField = self.upField = _div(children=[
            _div(className='toolbar', children=[
                _field('btnSgr', 'btn', className='toolbar-button armBtnRed'),
                toolbar.close_
            ]),
            _field('status', 'band', ['актив', 'архив', 'все'], recalcText=1, **style(margin='auto', display='table', width='auto'))
        ])

        # self.viewbar = _div(className='viewbarRA', children=self.setButtons)
        self.viewbar = self.makeViewbar(rightBtn=self.setButtons, **style(gridTemplateColumns='1px auto'))
        return self.shamrock(addUrl='&sgrId={sgrId}&status={status}')

    # *** *** ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        self.title = dcUK.title or 'ЛК куратора'
        sgr = well('sessionGr_Id', dcUK.unid)
        group = well('groups_groupId',sgr.nvgroup_id).title
        dcUK.doc.sgrId = dcUK.unid
        dcUK.doc.btnSgr = f"{sgr.title[:20]}|previewNew|form=SessionGr&title={group}&unid={dcUK.unid}&dbAlias=nv_SessionGr&rsMode=edit"

        dcUK.doc._view_ = 1

    # *** *** ***


