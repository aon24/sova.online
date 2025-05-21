# -*- coding: utf-8 -*-
'''
AON 19 jan 2018

'''
from arm.api.forms.formTools import style, _div, _btnD, _img, _teg

# *** *** ***

class Toolbar(object):

    def __init__(self, tx='', cmd='', par='', **attr):
        self.buttons = []
        if tx:
            self.addButton(tx, cmd, par, attr)

    def addButton(self, tx, cmd, par='', attr=None):
        a = {}
        if attr:
            for k, v in attr.items():
                if k == 'width':
                    a['style'] = {'width': v}
                else:
                    a[k] = v
        a['className'] = a.get('className', 'toolbar-button')
        self.buttons.append(_btnD(tx.replace(' ', '\xa0'), cmd, par, **a))
        self.toolbar = _div(className='toolbar', children=self.buttons)
        return self

    save = _btnD('СОХРАНИТЬ','save',title='Ctrl+S',className='toolbar-button')
    publish = _btnD('ОПУБЛИКОВАТЬ','publish',title='выложить на сайт',className='toolbar-button')
    close_ = _btnD('ЗАКРЫТЬ', 'close', title='[Esc] - закрыть окно', className='toolbar-button')

    close = _btnD('ЗАКРЫТЬ','close',title='[Esc] - закрыть окно',className='toolbar-button',**style(width='67mm'))
    close2 = _btnD('CLOSE','close',title='Esc',className='toolbar-button')
    saveClose = _btnD('СОХРАНИТЬ  И  ЗАКРЫТЬ','saveClose',
        title='[Shift+Esc] - сохранить и закрыть, [Ctrl-S] - только сохранить',className='toolbar-button')

    saveClose2 = _btnD('SAVE  AND  CLOSE'.replace(' ','\xa0'),'saveClose',title='Shift+Esc',className='toolbar-button')

    save2 = _btnD('SAVE','save',title='Ctrl+S',className='toolbar-button')
    prn = _btnD('', 'prn', title='Ctrl+P', className='tb-prn')
    edit = _btnD('Р Е Д А К Т И Р О В А Т Ь'.replace(' ', '\xa0'), 'edit', title='[Ctrl-Enter] - перейти в режим редактирования', className='toolbar-button', **style(width='67mm'))
    docSN = _btnD('\u2116 п/п', 'docSN', title='[Alt-1] Присвоить очередной № (для настройки нажмите кнопку при заполненном поле номера)', className='toolbar-button', **style(width='16mm'))
    searchByCorr = _btnD('Поиск', 'searchByCorr', title='Поиск обращений по заявителю и району', className='toolbar-button', **style(width='16mm'))

    red = _btnD('\xa0', 'setRed', **style(background='red', width=20), className='toolbar-button')
    green = _btnD('\xa0', 'setGreen', **style(background='green', width=20), className='toolbar-button')
    blue = _btnD('\xa0', 'setBlue', **style(background='blue', width=20), className='toolbar-button')
    black = _btnD('B', 'setBlack', **style(background='#aaa', width=20), className='toolbar-button')
    commentR = _btnD('Div', 'setDivR', **style(background='#fde', width=40), className='toolbar-button')
    commentB = _btnD('Div', 'setDivB', **style(background='#def', width=40), className='toolbar-button')

    hist = _btnD('\xa0Hist\xa0', 'tbHist', className='toolbar-button')
    profile = _btnD('P r o f i l e'.replace(' ', '\xa0'), 'tbProf', className='toolbar-button', **style(width='40mm'))
    tuning = _btnD('', 'showTuning', title='debug', className='tb-bag')

    # *** *** ***

    def info(self, mode):
        if mode in ['edit', 'new']:
            buttons = [self.saveClose, self.close]
        else:
            buttons = [self.close]
        return _div(className='toolbar', children=buttons)

    # *** *** ***

    def undo_redo(self, cmd, title):
        return _btnD('', cmd, title=title, className='toolbar-button',
                children=[
                    _div(className=f'{cmd}-circ', **style(borderRadius='50%', boxShadow='none', width=20, minWidth=20, height=20), children=[_div()]),
                    _div(name=cmd, className='tb-disable')
                ])

    cir9 = 'c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2'.join(['M4,6', 'M10,18', 'M4,18', 'M4,12', 'M10,12', 'M16,6', 'M10,6', 'M16,12', 'M16,18', 'z'])
    setting = _btnD('', 'setting', title='свойства страницы', className='toolbar-button',
        children=[
            _teg('svg', className='tb-props', focusable='false', viewBox='0 0 100 100', children=[_teg('path', d=cir9)]
        )])

    # *** *** ***

    def design(self, mode):
        buttons = [self.undo_redo('undo', 'назад Ctrl+Z'),
                   self.undo_redo('redo', 'вперед Ctrl+Y'),
                   self.save,
                   # self.publish,
                   self.close_,
                   self.setting,
                   self.tuning,
                   self.hist,
                ]

        if mode in ['edit', 'new']:
            return _div(id='mainToolbar', className='rtf-toolbar', children=[
                _div(className='rtf-bar', children=[_div(className='rtf-bar', children=buttons)])
            ])
        else:
            return _div(id='mainToolbar', className='toolbar', children=[self.close])

    def svg(self, mode):
        return _div(className='toolbar', children=[self.save2, self.saveClose2, self.close2, self.prn])

    def rkck(self, mode):
        if mode == 'preview':
            return 0

        elif mode == 'read':
            buttons = [self.edit, self.close, self.prn]

        elif mode in ['edit', 'new', 'newSd']:
            buttons = [self.docSN, self.saveClose, self.searchByCorr, self.close, self.prn]

        else:  # mode == 'readOnly':
            buttons = [self.close, self.prn]

        return _div(className='toolbar', children=buttons)

    # *** *** ***

    def o(self, mode):
        if mode == 'preview':
            return 0

        elif mode == 'read':
            buttons = [self.edit, self.close, self.prn]

        elif mode in ['edit', 'new']:
            buttons = [self.saveClose, self.close, self.prn]

        else:  # mode == 'readOnly':
            buttons = [self.close, self.prn]

        return _div(className='toolbar', children=buttons)

    # *** *** ***

    def readOnly(self, mode=None):
        if mode == 'preview':
            return 0

        return _div(className='toolbar', children=[self.close])

    # *** *** ***

    def rgb(self, mode='edit'):
        return _div(className='toolbar', children=[self.saveClose, self.red, self.green, self.blue, self.black, self.commentR, self.commentB, self.close])

    # *** *** ***

# *** *** ***

toolbar = Toolbar()

def saveClose():
    return _div(className='toolbar', children=[Toolbar.saveClose, Toolbar.close])

# *** *** ***


# *** *** ***
