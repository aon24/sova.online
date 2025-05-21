'''
Created on 2024

@author: aon24
'''
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import _field
from arm.api.forms.toolbars import toolbar
from arm.tools.common import setVersionFiles

from arm.settings import REPORT_DIR


# *** *** ***


class html(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'html'
        super().__init__(request)

# *** *** ***

    def page(self, request):
        return self.docPage([_field('html', 'json')], [toolbar.close_])

# *** *** ***

    def getJsCssUrl(self):
        return self.jsCssUrlRead + setVersionFiles(self.jsCssAdd, REPORT_DIR)

# *** *** ***

    def queryOpen(self, r):
        doc = r.dcUK.doc

        self.jsCssAdd = []
        doc.js and self.jsCssAdd.append(f'/api/jsv?{doc.js}')
        doc.css and self.jsCssAdd.append(f'/api/jsv?{doc.css}')

        for k in list(doc.keys()):
            if k not in ['HTML', 'UNID', 'REF', 'FULLNAME']:
                del doc._KV_[k.upper()]

        doc._view_ = '1'


