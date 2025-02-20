# -*- coding: utf-8 -*-
'''
AON 20 apr 2017

'''

from arm.api.forms.colors import htmlToPython

import json

# *** *** ***

fieldProps = ['blocking', 'addBtn', 'common', 'onDrop', 'onChange', 'onDrag', 'contextMenuCmdList', 'fd', 'xValue', 'br', 's2', 'classic', 'readOnly', 'edit', 'alias', 'saveAlias', 'sep', 'noPreview']


def navigator(form, cats, maxHeight=500):
    cat = _field('cat', 'list', list(cats), alias=1, className='navBtn', listItemClassName='rsvTop')

    # при вызове doc.changeDropList('subCat') в url подставится значение поля "CAT" вместо {FIELD}
    # при вызове doc.changeDropList('subCat', 'ss') в url подставится строка "ss" вместо {FIELD}
    subCat = _field('subCat', 'list', f'CAT|||/api/get/getData?cmd=getSubCats&form={form}&cat={{FIELD}}',
        **style(maxHeight=maxHeight, overflow='hidden auto', width='90%', margin='auto', display='block'),
        saveAlias=1, evenColor='#f4f8ff', default=-1)

    return _div(**style(paddingTop=5, position='relative'), children=[cat, subCat])


def sent():
    return _field('_sent', 'fd', **style(font='normal 8pt Courier'), br='br')


def docTitle(title, left=None, right=None, field=None):
    lch = _field(left[0], 'chb', [left[1]], name=left[0].upper(), **style(marginTop=-5)) if left else _div()
    if right:
        rch = _field(right[0], 'chb', [right[1]], name=right[0].upper(), **style(marginTop=-5))
        if len(right) == 3:
            rch['fieldProps'] = {right[2]: 1}
    else:
        rch = _div()
    center = _field(field, 'fd', 'variable') if field else _div(title)

    return _div(className='cell-title', **style(padding=2), children=[lch, center, rch])


def infoPage(request):
    from arm.api.forms.toolbars import toolbar
    if request.dcUK.mode == 'preview':
        hPage = 'calc(100% - 30px)'
    else:
        hPage = '99vh'
    return _div(
        **style(overflow='hidden', height=hPage),  # backgroundImage='url(image/24x24LB.png)',
        children=[
            toolbar.info(request.dcUK.mode),
            _div(**style(width='100%', height='calc(100% - 30px)', margin='30px auto 0', overflow='auto'),
                children=[_field('_fields_FD', 'json')]),
        ]
    )


def infoQueryOpen(dcUK):
    if not dcUK._superUser:
        dcUK.doc._fields_FD = json.dumps([labelc('info')], ensure_ascii=False)
        return

    ls = []
    i = 0
    for fi in sorted(dcUK.doc.keys()):
        i += 1
        bg = '#f0f8ff' if i % 2 else '#f0fff8'
        if fi.startswith('FILES'):
            field = _div(**style(backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(fi, className='label', **style(font='bold 12pt Courier')),
                    _field(fi, **style(font='bold 12pt Courier', color='#048'))]
                )
        elif fi in ['ROOT', 'RTF']:
            field = _div(**style(display='table', width='100%', backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(f'{fi}:{str(len(dcUK.doc[fi]))}', className='label', **style(display='table-cell', font='bold 12pt Courier', width=200)),
                    _div(),
                    # _div(str(len(dcUK.doc[fi])), className='label', **style(display='table-cell', font='bold 12pt Courier')),
                ]
            )
        else:
            field = _div(**style(display='table', width='100%', backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(fi, className='label', **style(display='table-cell', font='bold 12pt Courier', width=130)),
                    _field(fi, **style(display='table-cell', font='bold 12pt Courier'))]
                )

        ls.append(field)

    dcUK.doc._fields_FD = json.dumps(ls, ensure_ascii=False)


def _search():
    return [
            _btnD('×', 'reset', className='reset', title='сбросить результаты '),
            _field('search', 'tx', edit=1, placeholder='поиск', kbEnter='search', skipEnter=1,
                    **style(width=150, maxHeight=35, overflow='hidden', margin='0 2px')),
            _btnD('►', 'search', className='_', title='искать (Enter) '),
    ]


def _tabNew(*, xName='tabNew_FD', tabs=None, labWidth=200):
    '''
    tabs: [ [label, body_div, lavel-width], ...]
    in js add:

        for (let i=0; i < 10; i++)
            window.sovaActions.<form>.hide[`<xName>_${i}`] = doc => i !== doc.getField(`<xName>_${i}`);
    '''
    header = []
    body = []
    i = w = 0
    for it in tabs:
        if it and it[1]:
            lw = it[2] if len(it) > 2 else labWidth
            w += lw
            header.append(f'{it[0]}:{lw}')
            body.append(_div(name=f'{xName}_{i}', children=[it[1]]))
            i += 1
    return  _div(className='tabNew', children=[
                _div(className='tnHeader', children=[
                    _div(className='tnLast'),
                    _field(xName, 'band', header, **style(width=w), className='tnBand'),
                    _div(className='tnLast')
                ]),
                _div(className='tnBody', children=body)
            ])


def _chbVFM(pk):
    return _div(children=[
        _teg('input', type='checkbox', id=f'chb_{pk}', className='chbVN'),
        _teg('label', _for=f'chb_{pk}')
    ])


def _chbVF(pk):
    return  (_teg('input', type='checkbox', id=f'chb_{pk}', name='chbFV', className='checkboxFV'),
        _teg('label', _for=f'chb_{pk}'))
            

def _btn1(letter, cmd, right=None, left=None, title=''):
    style = None
    if right: style = dict(right=right)
    if left: style = dict(left=left)

    return _btnD(letter, cmd, title=title, className='mBtn fv1', style=style)


def _btn2(letter, cmd, param, right=None, left=None, title='', yes='', name=None):
    style = None
    yes = yes and 'fv2yes'
    if right: style = dict(right=right)
    if left: style = dict(left=left)

    return _btnD(letter, cmd, param, name=name, title=title, className=f'mBtn2 fv2 {yes}', style=style)


def _btnNew(dbAlias='', style=None, cmd=None, name=None):
    style = (style and dict(style)) or {}
    return _btnD('', cmd or 'cmdNew', dbAlias, className=' ', style=style, name=name,
        children=[_img(title='создать новый документ', style=dict(height='100%', width=28), src='/image/new.png')])


def _btnCopyRing(cmd, pk):
    return _btnD('C', cmd, pk, title='скопировать документ', className='btnIcon mBtn fvc')


def _btnDel(cmd, pk):
    return _btnD('\xd7', cmd, pk, title='удалить', className='btnIcon mBtn fva')


def _btnCopy(cmd, pk):
    return _btnD('\xa0', cmd, pk, title='скопировать документ', className='btnIcon btnCopy')


def _btnEdit(cmd, pk):
    return _btnD('\xa0', cmd, pk, title='изменить', className='btnIcon btnEdit')


def _btnPref(cmd, pk):
    return _btnD('\xa0', cmd, pk, title='профайл студента', className='btnIcon btnPref')


def _btnView(cmd, pk):
    return _btnD('\xa0', cmd, pk, title='превью', className='btnIcon btnView')


def _btnPreview(cmd, pk):
    return _btnD('V', cmd, pk, title='превью', className='btnIcon mBtn fvb')


def _mainPage(**kv):
    kkv = {}
    kkv.update(kv)
    focus = kkv.get('focus')
    if focus:
        del kkv['focus']
        return _div(focus=focus, children=[_div(**kkv)])
    else:
        return _div(children=[_div(**kv)])


def _div(tx=None, **kv): return _teg('div', tx, **kv)


def _form(**kv): return _teg('form', **kv)


def _input(**kv): return _teg('input', **kv)


def _textarea(tx=None, **kv): return _teg('textarea', tx, **kv)


def _b(tx=None, **kv): return _teg('b', tx, **kv)


def _i(tx=None, **kv): return _teg('i', tx, **kv)


def _p(tx=None, **kv): return _teg('p', tx, **kv)


def _span(tx=None, **kv): return _teg('span', tx, **kv)


def _ul(tx=None, **kv): return _teg('ul', tx, **kv)


def _ol(tx=None, **kv): return _teg('ol', tx, **kv)


def _li(tx=None, **kv): return _teg('li', tx, **kv)


def _a(tx=None, **kv): return _teg('a', tx, **kv)


def _lc(text, **p):
    return _teg('div', text, className='lc', **p)


def _teg(teg, text=None, **kv):
    tg = {'_teg': teg}
    atr = {}
    fpr = {}
    if text:
        tg['text'] = text
    for k, v in kv.items():
        if v:
            if k == 'skip':
                return None
            elif k == 'children':
                tg['children'] = v
            elif k in fieldProps:
                fpr[k] = v
            elif k == '_for':
                atr['htmlFor'] = v
            else:
                atr[k] = v
    if atr:
        tg['attributes'] = atr
    if fpr:
        tg['fieldProps'] = fpr
    return tg


def _btnD(*p, **kv):
    return None if kv.get('skip') else _button(*p, div=True, **kv)


def _button(*p, div=None, **kv):
    tg = {'_teg': 'button', 'text': p[0]}
    if len(p) > 1:
        tg['fieldProps'] = {'_cmd': p[1]}
    if div:
        tg['fieldProps']['_div'] = 1
    if len(p) > 2:
        tg['fieldProps']['_param'] = p[2]

    atr = {}
    for k, v in kv.items():
        if v:
            if k == 'children':
                tg['children'] = v
            elif k in fieldProps:
                tg['fieldProps'][k] = v
            else:
                atr[k] = v

    if atr:
        tg['attributes'] = atr
    return tg


def _img(**attr):
    return {'_teg': 'img', 'attributes': {**attr} }


def _h2(tx, **attr):
    return _teg('h2', tx, **attr)


def _h3(tx, **attr):
    return _teg('h3', tx, **attr)


def _br():
    return {'_teg': 'br'}


def _table(*tables, rowStyle=None, skip=None):  # создает несколько таблиц
    if skip:
        return None

    ls = [] # список таблиц
    for t in tables:
        tabl = dict(r=[], rowStyle=None) # создаем таблиц, где r-ряды, rowStyle-ее стиль
        for row in t:
            if type(row) is dict and row.get('rowStyle'):
                tabl['rowStyle'] = row.get('rowStyle')
            else:
                tabl['rowStyle'] = tabl.get('rowStyle', rowStyle)
                tabl['r'].append(row)
        tabl['r'] and ls.append(tabl)
    return [_div(style=t['rowStyle'], className='rowf', children=t['r']) for t in ls]


def _table_1(*rows, style=None, rowStyle={}, skip=None, **par):  # создает таблицу rows - строки таблицы
    if skip:
        return None

    ls = [] # список tr
    for r in rows:
        for cell in r:
            cell['attributes'] = cell.get('attributes', {})
            cell['attributes']['style'] = cell['attributes'].get('style', {})
            cell['attributes']['style']['display'] = 'table-cell'
        ls.append(
            _div(style=dict(**rowStyle, display='table-row'), children=r)
        )
    return _div(style=style, className='rowf', children=ls, **par)


def style(s='style', **par):
    return {s: {**par}}


def gridStyle(s, **kv):
    return {'style': dict(display='grid', gridTemplateColumns=s, **kv)}


def labeldc(l=None, **kv):
    if kv.get('skip'):
        return None
    att = dict(className='labeldc')

    for k, v in kv.items():
        if k == 'style':
            if 'style' in att:
                att['style'].update(v)
            else:
                att['style'] = v
        else:
            att[k] = v
    return _div(l or '\xa0', **att)


def label(l=None, **kv):
    if kv.get('skip'):
        return None
    att = dict(className='label')

    for k, v in kv.items():
        if k == 'style':
            if 'style' in att:
                att['style'].update(v)
            else:
                att['style'] = v
        else:
            att[k] = v
    return _div(l or '\xa0', **att)


def label_(l=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'label_ label'
    return label(l, **atr)


def labell(l=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'labell label'
    return label(l, **atr)


def labelc(l=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'labelc label'
    return label(l, **atr)


def _lf(lab, *p, **pp):
    if pp.get('skip'):
        return None
    return _div(children=[labell(lab), _field(*p, **pp)])


def labField(l, fname, ftype='tx', flab=None, **par):
    if par.get('skip'):
        return None
    return [label(l, name=par.get('name')), _lbf(fname, ftype, flab, **par)]


def labField_(l, fname, ftype='tx', flab=None, **par):
    if par.get('skip'):
        return None
    return [label_(l, name=par.get('name')), _lbf(fname, ftype, flab, **par)]


def _lbf(fname, ftype='tx', flab=None, **kv):
    fname = fname.upper()
    if 'dropList' in kv:
        tg = {'field': (fname, ftype, kv['dropList'])}
    elif flab or type(flab) is list:
        tg = {'field': (fname, ftype, flab)}
    else:
        tg = {'field': (fname, ftype)}

    atr = {}
    fpr = {}
    for k, v in kv.items():
        if v:
            if k == 'children':
                tg['children'] = v
            elif k in fieldProps:
                fpr[k] = v
            elif k == '_for':
                atr['htmlFor'] = v
            elif k != 'dropList':
                atr[k] = v
    if atr:
        tg['attributes'] = atr
    if fpr:
        tg['fieldProps'] = fpr

    return tg


def _field(*p, **dp):
    if dp.get('skip'):
        return None
    return _lbf(*p, **dp)

def _fileShow(fname, **kv):
    if kv.get('skip'):
        return None
    return _lbf(fname, 'fileShow', **kv)

# *** *** ***


def _tab(*, width=100, height='calc(100% - 3px)', ah=0, tabs=None):
    '''
    width - width of headeritem
    tabs: [ [label, body_div], ...]
    '''
    header = []
    body = []

    i = 0
    for it in tabs:
        if it and it[1]:
            w = it[2] if len(it) > 2 else width
            cn = 'tabItem' if i else 'tabItemSel'
            name = it[3] if len(it) > 3 else None
            header.append(_btnD(it[0], f'cmdTab_{i}', i, className=cn, **style(width=w), name=name))
            body.append(_div(name=f'TABLEBODY_{i}', children=[it[1]]))
            i += 1

    header.append(_div(className='tabItemLast'))

    return  _div(className='tabNew', children=[
                _div(className='tabHeader', children=header),
                _div(className='tabBody', children=body)
            ])

# *** *** **

