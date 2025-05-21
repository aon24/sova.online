'''
Created on 2024

@author: aon24
'''
from arm.api.forms.formTools import style, _div, _btnD, _lc, _field, labField, _a
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

# *** *** ***


class etc(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'
        self.title = 'Настройки'
        self.noCaching = True

        super().__init__(request)

# *** *** ***

    def office(self):
        return _div(
            children=[
            _div(**style(margin='10px auto', height=1, width=250, border='0 solid #036', borderTopWidth=1)),

            _btnD('Справочники',
                'previewArm', 'newForm=v_classifiers&title=Справочники',
                className='rsvTop', **style(width=150, margin='10px auto')),
            _btnD('Р А С С Ы Л К И', 'exportEmail', className='rsvTop',
                **style(width=150, margin='10px auto')),
            _btnD('3 D L', 'previewArm', 'newForm=v_more&title=Лендинговые страницы',
                title='Лендинговые страницы', className='rsvTop',
                **style(width=150, margin='10px auto')),

            _div(**style(margin='4px auto', height=1, width=250, border='0 solid #036', borderTopWidth=1)),

            _btnD('Life', 'loadWell', **style(width=150, margin='10px auto'), title='Перезагрузка справочников', className='rsvTop'),
            _btnD('Log', 'xopen', '/api/new?form=ilog', **style(width=150, margin='10px auto'), title='syslog', className='rsvTop'),
            _a('Admin', href='/admin', **style(margin='10px auto')),
        ])

    def page(self, request):
        _etc = [
            _div(**style(height='100%', overflow='auto', textAlign='center'), children=[
                _lc('Размер'),
                _field('scale_ETC', 'band', ['50%', '75%', '90%', '100%', '110%', '125%', '150%', ],
                    **style(maxWidth=300, margin='auto')
                ),
                _div(**style(maxWidth=300, margin='auto', gap='10px', display='grid', gridTemplateColumns='1fr 100px'),
                    children=[
                        *labField('Показать текст вместо иконок', 'noicons_etc', 'chb', ['да'], edit=1),
                        *labField('Изменять размер окна окна', 'eMovePl_etc', 'chb', ['да'], edit=1),
                        *labField('Автоматически сохранять положение окон', 'eSavePl_etc', 'chb', ['да'], edit=1),
                ]),

                _div(**style(textAlign='center', marginTop=15), children=[
                    _btnD('\xa0запомнить\xa0', 'save_etc', className='toolbar-button'),
                    _btnD('\xa0очистить\xa0', 'reset_etc', className='toolbar-button'),
                ]),

                request.dcUK._staff and self.office()
            ])
        ]
        
        return self.docPage(_etc, tool=[toolbar.close_])

# *** *** ***

