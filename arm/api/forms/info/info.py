# -*- coding: utf-8 -*-
'''
AON 20 apr 2017

'''

from ..formTools import infoPage, infoQueryOpen
from ..classPage import Page

import json

# *** *** ***

class info(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Info'
        self.dbAlias = 'no'
        super().__init__(request)

    def page(self, request):
        return infoPage(request)

# *** *** ***

    def queryOpen(self, dcUK):
        infoQueryOpen(dcUK)

# *** *** ***

