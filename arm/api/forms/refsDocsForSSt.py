'''
Created on 2024

@author: aon24
'''
from arm.api.forms.formTools import _b, _span, style, _btnD


def refsDocsForSSt(pk, docSGr, doc, cmdEdit):
    i = 1
    rf = []
    while docSGr[f'status_{i}']:
        d1 = docSGr[f'DATE_BEGIN_{i}']
        d1 = f'{d1[-2:]}.{d1[5:7]}'
        title = docSGr[f'title_{i}']
        title = title and title[0] + ': '
        ls = (docSGr[f'LECTOR_{i}'] + '_ _ _').split(' ')
        lector = f'{ls[0]} {ls[1][0]}.{ls[2][0]}.'
        if doc[f'allow_{i}']:
            allow = _span('есть', **style(color='#00f'))
        else:
            allow = _span('нет', **style(color='#f00'))

        if doc[f'pass_{i}']:
            pas = _span('да', **style(color='#00f'))
        else:
            pas = _span('нет', **style(color='#f00'))

        if doc[f'test_{i}']:
            test = _span('есть', **style(color='#00f'))
        else:
            test = _span('нет', **style(color='#f00'))

        part = _btnD('', cmdEdit, pk, s2=1, br=1, className='rCell', children=[
            _b(children=[
                _span(d1),
                _span(doc[f'DURATION_{i}'] + '\xa0', **style(color='#840')),
                _span(title + lector),
            ]),
            # _br(),
            _span(' Доп.: ', **style(color='#aaa')), allow,
            _span(' Был: ', **style(color='#aaa')), pas,
            _span(' Зач.: ', **style(color='#aaa')), test,
        ])

        rf.append([f'{pk}-{i}', '', part])
        i += 1
    return rf

