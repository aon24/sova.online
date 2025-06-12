'''
Created on 2024

@author: aon24
'''
from arm.tools.DC import well, swell
from arm.tools.first import err
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import labField, style, labell, _div, _field, gridStyle, docTitle

# *** *** ***

def sw(w):
    return {'style': {'width': w}}


class Module(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'
        self.title = 'LM'
        super().__init__(request)

# *** *** ***
    def page(self, request):
        o = _div(**style(width=785, margin='auto'), children=[
    
            docTitle('Загружаемый модуль', left=['turn_on', 'включен'], right=['runFD', 'выполняется', 'readOnly']),
 
            _div(className='cellbg-lite', children=[
                _div(**gridStyle('100px 1fr'), children=labField('Назначение', 'title')),
                _div(**gridStyle('100px 1fr 50px 140px 60px 180px'), children=[
                    *labField('Расписание', 'SCHEDULED', 'lbsd', swell('scheduled'), alias=1),
                    *labField('День', 'SCHEDDAY', 'lbsd', '', alias=1),
                    *labField('Время', 'SCHEDTIME', 'lbsd', '', alias=1),
                ]),
                _div(**gridStyle('100px 1fr'), children=labField('', 'runByStart', 'chb', ['Выполнить при сохранении']))
            ]),

            _div(className='cellbg-lite', children=[
                labell('Python module in the directoty "nv_lm/agents"'),
                _field('module', 'tx', **style(font='normal 16px Courier')),
                labell('Parameter: string'),
                _field('param', 'tx', **style(font='normal 16px Courier'))
            ]),

            _div(className='cellbg-lite', children=[
                _div(**gridStyle('1fr 1fr 1fr 1fr'), children=[
                    *labField('Время старта', 'starting_time', 'fd'),
                    *labField('Время окончания', 'end_time', 'fd'),
                ])
            ]),
            self.noteStatus(),
            _div(className='cellbg-lite', children=[_field('log', 'fd', fd=1, br=1)])
        ])

        return self.docPage([o])

# *** *** ***

    def queryOpen(self, r):
        doc = r.dcUK.doc
        doc.status = doc.status or 'active'
        doc.log = doc.log
        for k in doc.keys():
            if k.startswith('REPORT_'):
                doc.log += f'{k}: {doc[k]}\n'

# *** *** ***

    def querySave(self, dcUK):
        if dcUK._SUPERUSER:
            dcUK.doc.starting_time = dcUK.doc.end_time = dcUK.doc.log = ''
            return True
        else:
            err(f'Access denied for {dcUK.fullName}', cat='querySave')

# *** *** ***

