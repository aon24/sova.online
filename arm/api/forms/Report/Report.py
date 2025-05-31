# -*- coding: utf-8 -*- 
'''
AON 18 apr 2017

'''
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.api.forms.formTools import labField, _div, log, gridStyle, docTitle

# *** *** ***


class Report(Page):
    def __init__(self, request):
        self.title = 'Отчет'
        self.form = 'Report'
        self.dbAlias = 'nv_lm_Module'
        super().__init__(request)


    # *** *** ***

    def page(self, request):
        fields = [
            docTitle('Отчет'),
                _div(readOnly=1, **gridStyle('140px 1fr'), children=[
                    *labField('Отчет', 'nodafd', fd=1),
                    *labField('Запуск отчета', 'starting_time'),
                    *labField('Окончание', 'end_time'),
                    *labField('Пользователь', 'CREATOR'),

                    *labField('Категория', 'REPORTCAT'),
                    *labField('Название', 'REPORTNAME'),
                    *labField('Заголовок', 'REPORTTITLE'),
                    *labField('Начало периода', 'dt1'),
                    *labField('Конец периода', 'dt2'),
                    *labField('Начало периода 2', 'dt3'),
                    *labField('Конец периода 2', 'dt4'),
                    *labField('Журналы', 'LBYEARS'),
                    *labField('Префиксы', 'GRGROUP'),
                    *labField('Формула отбора', 'QUERYMAIN'),
                    *labField('Комментарий', 'NOTES'),
            ]),
            log(),
        ]

        return self.docPage(fields, [toolbar.close_])

    # *** *** ***
    
    def queryOpen(self, r):
        d = r.dcUK.doc
        d.nodafd = '№ ' + d.id + ' от ' + d.D('_created')
        d._log = d._log.replace('<br>', '\n')
    
# *** *** ***
