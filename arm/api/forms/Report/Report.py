# -*- coding: utf-8 -*- 
'''
AON 18 apr 2017

'''
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.api.forms.formTools import labField, _div, log, gridStyle, docTitle

# *** *** ***


class Report(Page):
    '''
    Форма отображает документ в бд nv_lm таблица Module
    CRM - форма описание отчета (не сам отчет).
    Отчет формируется в отдельном процессе по расписанию или сразу при сохранении
    и отображается в виде как подчиненный документ к этой форме
    '''

    title = 'Отчет'
    form = 'Report'

    def __init__(self, request):
        self.dbAlias = 'nv_lm_Module'
        super().__init__(request)

    #  *** *** ***

    def page(self, request):
        fields = [
            docTitle('Отчет'),
            _div(readOnly=1, **gridStyle('140px 1fr'), children=[
                *labField('Отчет', 'nodafd', fd=1),
                *labField('Запуск отчета', 'starting_time'),
                *labField('Окончание', 'end_time'),
                *labField('Расписание', 'SCHEDULED'),
                *labField('Пользователь', '_CREATOR'),

                *labField('Категория', 'title'),
                *labField('Название', 'FIRSTLIST'),
                *labField('Параметры', 'addLIST'),
                *labField('Начало периода', 'dt1'),
                *labField('Конец периода', 'dt2'),
                *labField('Начало периода 2', 'dt3'),
                *labField('Конец периода 2', 'dt4'),
                *labField('Комментарий', 'NOTES'),
            ]),
            log(),
        ]

        return self.docPage(fields, [toolbar.close_])

    # *** *** ***

    def queryOpen(self, r):
        d = r.dcUK.doc
        d.nodafd = '№ ' + d.id + ' от ' + d.D('_created')
        d.log = d.log.replace('<br>', '\n')

# *** *** ***
