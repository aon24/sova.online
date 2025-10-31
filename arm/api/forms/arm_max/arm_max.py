'''
Created on 2020.

@author: aon
'''
from arm.api.forms.formTools import _field, _div, style, gridStyleRows
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

# *** *** ***


class arm_max(Page):
    '''
    Форма для просмотра сводки(быстрых отчетов) во весь экран. Вызывается из сводки
    кнопкой openMax = _btnD('ОТКРЫТЬ СВОДКУ', 'openMax', select=1, className='btnClose')
    '''
    _VIEW_ = 1  # forbidding saving

    def __init__(self, request):
        self.form = 'arm_max'
        self.jsCssUrlEdit = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        super().__init__(request)

    def page(self, request):
        return _div(**gridStyleRows('auto 1fr', height='calc(100% - 25px)'),
                    children=[
                        _div(className='toolbar', children=[toolbar.close_]),
                        _div(className='arm_max', **style(overflow='auto', height='100%', width='100%', margin='auto'), children=[
                            _field('body', 'json', **style(background='#f8f8f8'))
                        ])
                ])

    # *** *** ***
