'''
Created on 2024

@author: aon24
'''
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import _field
from arm.api.forms.toolbars import toolbar
from arm.tools.common import setVersionFiles

import os

# *** *** ***
'''
создается в отчетах и агентах
'''


class html(Page):
    '''
    Форма из 1 поля и кнопки "Закрыть" для показа отчетов
    Отчеты формируются в бд nv_reports(reports.sqlite3) таблица nv_reports.report
    '''
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'html'
        super().__init__(request)

# *** *** ***

    def page(self, request):
        return self.docPage([_field('main', 'json')], [toolbar.close_])

# *** *** ***

    def getJsCssUrl(self, request):
        fn = os.path.join('/api/jsv?nv_reports', request.dcUK.doc.jsCss)
        return self.jsCssUrlRead + setVersionFiles(fn, '')

# *** *** ***
