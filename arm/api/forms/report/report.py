# -*- coding: utf-8 -*- 
'''
AON 18 apr 2017

'''
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.api.forms.formTools import labField, _div, sent, gridStyle, docTitle

# *** *** ***

class report(Page):
    def __init__(self, form):
        self.title = 'Отчет'
        self.form = 'report'
        self.dbAlias = 'reports'
        super().__init__(form)


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
            sent(),
        ]

        return self.docPage(fields, [toolbar.close_])

    # *** *** ***
    
    def queryOpen(self, dcUK):
        d = dcUK.doc
        d.nodafd = '№ ' + d.id + ' от ' + d.D('_created')
        d._log = d._log.replace('<br>', '\n')
    
# *** *** ***
