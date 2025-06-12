# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well
from arm.tools.common import today

from ..formTools import labField, style, _div, _field, label, labelc, _h2, _span
from ..classPage import Page

# *** *** ***


class Payment(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Оплата'
        self.dbAlias = 'nv_Payment'

        super().__init__(request)

    # ***

    def page(self, request):
        fields = [
            _h2('Платеж',**style(textAlign='center',margin=0,letterSpacing=2)),
            _div(**style(textAlign='center'),children=[
                _field('fio_fd', 'fd', className='h3'),
                _field('phone_fd', 'fd', **style(display='block')),  # , textAlign='center'
                _div(**style(display='inline-block'), children=labField('сумма', 'summa', 'tx')),
                _div(**style(display='inline-block'),children=labField('группа','group',readOnly=1,**style(width=150))),

                labelc('оплата за 1 месяц или за период'),
                _field('t1', 'dt', **style(display='inline-block')),
                _span(' \xA0 '),
                _field('t2', 'dt', **style(display='inline-block')),

                _field('cash','band',['нал','безнал','QR'],recalcText=1,**style(margin='auto',width='auto',borderSpacing=10)),

                labelc('дата платежа'),
                _field('pay_date', 'dt', **style(margin='auto')),

                label('назначение платежа'),
                _field('nvEvent', 'tx', readOnly=1,
                    **style(color='#036', fontWeight=700, margin='5px 0', width=230)
                ),
                _field('purpose', 'lbme', '/api/well?clues=sessionTmpl_nve_band|1'),
            ]),
            self.noteStatus(),
        ]

        return self.docPage(fields)

    # ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        d = dcUK.doc
        d.pref = d.pref or dcUK.profile
        prof = well('profiles',d.pref)

        if dcUK.mode == 'new':
            d.pay_date = today('-')
            d.fio = prof.full_name
            d.phone = prof.phone
            d.status = 'active'

            if dcUK.sgrId:  # create from SessionSt-form
                sgr = well('sessionGr_Id', dcUK.sgrId)
                d.nvEvent = well('eventsByCode', sgr.nvEvent)
                d.nvgroup = sgr.nvgroup
                d.group = well('groups_groupId', sgr.nvgroup).title
                d.purpose = sgr.title
                d.t1 = sgr.DATE_BEGIN
            else:
                gr = prof.student_groups
                gr = gr.partition('\n')[0]
                d.group, _, d.nvgroup = gr.partition('|')

        elif not d.group and prof.student_groups:
            d.group, _, d.nvgroup = prof.student_groups.partition('\n')[0].partition('|')

        d.fio_fd = d.fio
        d.phone_fd = d.phone

    def querySave(self, dcUK):
        return True

    # ***

