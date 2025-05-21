# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
'''
from arm.api.forms.formTools import style, _div, _field, _btnD, _table, _span, _br, label
from arm.api.forms.classPage import Page

# *** *** ***

class a_colors(Page):
    def __init__(self, request):
        self.title = 'colors'
        self.form = 'a_colors'
        self.jsCssUrlEdit = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        super().__init__(request)

    def page(self, request):
        return _div(className='color-head', children=[
            _div(name='setColor', children=[
                _div(className='setting-head', name='setColorWP', children=[_span('Заливка\xa0для\xa0всех\xa0стен', className='setting-title')]),
                _div(className='setting-head', name='phoneB', children=[_span('Фон', className='setting-title')]),
                _div(className='setting-head', name='wallsColor', children=[_span('Цвет этой стены', className='setting-title')]),
                _div(className='setting-head', name='wallsPaperColor', children=[_span('Обои для всех стен', className='setting-title')]),
                _div(className='setting-head', name='m3tableColor', children=[_span('Цвет всех граней', className='setting-title')]),
                _div(className='setting-head', name='fasadeColor', children=[_span('Цвет фасада', className='setting-title')]),
                _div(className='setting-head', name='edgeColor', children=[_span('Цвет грани', className='setting-title')]),
    
                self.setColor(),
            ]),
            
            *self.grid()
            
        ])

    # *** *** ***
    
    def grid(self): # 'Сетка'
        return [
            _div(className='setting-line'),
            _div(className='setting-head', children=[
                _span('Сетка', className='setting-title'),
                _field(f'grid', 'chb3', ['задать|set', 'наследовать|inherit'], **style(width='100%', margin='5px auto')),
            ]),
            _div(name='grid', children=[
                *_table([
                    _field('gridX', 'slip', [-300, 300, 10, 'шаг вертик.', 3000, -3000], className='label'),
                    _field('gridY', 'slip', [-300, 300, 10, 'шаг гориз.', 3000, -3000], className='label'),
                ],[
                    _field('gridWidth', 'slip', [0, 100, 1, 'Ширина'], className='label', **style(width='50%', margin='7px auto')),
                    label('Цвет', **style(paddingTop=10)),
                    _field(f'gridColor', 'input-color', colorList='rainbow')
                ])
            ]),
        ]
        
    # *** *** ***
    
    def setColor(self, adf=''):
        return _div(children=[
            _field(f'bgStyle{adf}', 'chb3', ['цвет|color', 'картинка|image'], **style(width='100%', margin='5px auto')),
            _div(name=f'bgColor{adf}', children=self.bgColor(adf), className='setting-block'),
            _div(name=f'bgImage{adf}', children=self.bgImage(adf), className='setting-block'),
            _div(**style(height=1))
        ])

    # *** *** ***

    def bgColor(self, adf):
        return [
            *_table([
                _div(**style(width='20%', textAlign='center'), children=[
                    _span('Цвет', **style(textAlign='center', font='bold 9pt Verdana, Arial', color='#036')),
                    _field(f'backgroundColor{adf}', 'input-color', colorList='rainbow')
                ]),
                _div(**style(padding='0 10px', textAlign='center', borderLeftWidth=1, border='0 solid #aaa'), children=[
                    _field(f'gradient{adf}', 'chb', ['градиент'], **style(marginTop=10, float='left', font='bold 9pt Verdana, Arial', color='#036')),
                    _field(f'gradientColor{adf}', 'input-color', name=f'gradient{adf}', colorList='rainbow'),
                    _br(),
                    _field(f'gradientDeg{adf}', 'slip', [0, 360, 15, 'Наклон'], name=f'gradient{adf}', className='label', **style(width=160)),
                ]),
            ]),
        ]

    # *** *** ***

    def bgImage(self, adf):
        return [
            *_table(
                [
                    _btnD('Выбрать из файла', 'openImg', **style(padding=3, lineHeight=1, boxShadow='#00448866 0 0 5px 1px')),
                    _btnD('Вставить ссылку', 'imgFromBuf', **style(padding=3, lineHeight=1, boxShadow='#00448866 0 0 5px 1px')),
                ],
                [    _div(**style(height=5))],
                [
                    _field(f'backgroundImage{adf}', 'tx', readOnly=1, placeholder='скопируйте сюда url-ссылку'),
                    _btnD('×', 'clrUrl', title='очистить поле', **style(width=20, height=1, color='red', verticalAlign='middle'))
                ],
                [
                    _field(f'bgiSizeX{adf}', 'slip', [0, 100, 10, 'X', 10000], className='label', metric='px|%', xValue=100),
                    _field(f'bgiSizeY{adf}', 'slip', [0, 100, 10, 'Y', 10000], className='label', metric='px|%', xValue=100),
                ],
                [
                    _field(f'repeatX{adf}', 'chb', ['повтор X|repeat'], className='label'),
                    _field(f'repeatY{adf}', 'chb', ['повтор Y|repeat'], className='label')
                ],
        **style('rowStyle', width='100%', margin=0, borderSpacing='4px 0px')
        )]

    # *** *** ***

