# -*- coding: utf-8 -*-
'''
AON 20 apr 2017

'''

from ..formTools import infoPage, infoQueryOpen
from ..classPage import Page

# *** *** ***


class info(Page):
    '''
    Форма позволяет посмотреть поля документа(если есть права офиса или суперп.)
    Форму можно вызвать заменив в урл значение ключа form на info или значение ключа mode на info
    '''
    title = 'Info'
    dbAlias = 'no'

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']

        super().__init__(request)

    def page(self, request):
        return infoPage(request)

# *** *** ***

    def queryOpen(self, r):
        infoQueryOpen(r)

# *** *** ***
