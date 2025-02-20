'''
Created on 2024

@author: aon24
'''

from arm.api.forms.formTools import style, _div, _field, labField

# *** *** ***


def header(dcUK):
    return _div('header')

# *** *** ***


def main(dcUK):
    return _div(**style(padding=5), children=[
        *labField('Ссылки на видеофайлы', 'videoList', kbEnter='setVideoGrid'),
        _div('Видеоматериалы', className='h2'),
        _field('videoGrid_FD', 'grid', xmin=160, xmax=230),
    ])


# *** *** ***
def nav(dcUK):
    return _field('nav', 'rtf')


# *** *** ***
def footer(dcUK):
    return _div('footer')

# *** *** ***
