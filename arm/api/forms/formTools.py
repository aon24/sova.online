'''
AON 20 apr 2017

'''

import json

# *** *** ***

fieldProps = ['_cmd', '_param', 'fileName', 'short', 'noAlias', 'rowLength', 'recalcText',
              'btnD', 'blocking', 'addBtn', 'common', 'onDrop', 'onChange', 'onDrag',
              'contextMenuCmdList', 'fd', 'xValue', 'br', 's2', 'chbView', 'readOnly',
              'edit', 'alias', 'saveAlias', 'sep', 'noPreview']


def log():
    return _field('log', 'fd', **style(font='normal 8pt Courier'), br='br')


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


def infoPage(mode):
    from arm.api.forms.toolbars import toolbar
    return _div(
        children=[
            toolbar.info(mode),
            _field('_fields_FD', 'json', **style(overflow='auto', maxHeight='calc(100% - 45px)'))
        ]
    )


def infoQueryOpen(r):
    dcUK = r.dcUK
    if not dcUK._superUser:
        dcUK.doc._fields_FD = json.dumps([labelc('info')], ensure_ascii=False)
        return

    ls = []
    i = 0
    for fi in sorted(dcUK.doc.keys()):
        i += 1
        bg = '#f0f8ff' if i % 2 else '#f0fff8'
        if fi.startswith('FILES'):
            field = _div(
                **style(backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(fi, className='label', **style(font='bold 12pt Courier')),
                    _field(fi, **style(font='bold 12pt Courier', color='#036'))]
                )
        elif fi in ['ROOT', 'RTF']:
            field = _div(
                **style(display='table', width='100%', backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(f'{fi}:{str(len(dcUK.doc[fi]))}', className='label', **style(display='table-cell', font='bold 12pt Courier', width=200)),
                    _div(),
                ]
            )
        else:
            field = _div(
                **style(display='table', width='100%', backgroundColor=bg, border='1px solid #aaa', borderTopWidth=0, padding=3),
                children=[
                    _div(fi, className='label', **style(display='table-cell', font='bold 12pt Courier', width=130)),
                    _field(fi, **style(display='table-cell', font='bold 12pt Courier'))]
                )

        ls.append(field)

    dcUK.doc._fields_FD = json.dumps(ls, ensure_ascii=False)


def _search():
    return [
            _btnD('×', 'reset', className='reset', title='сбросить результаты '),
            _field(
                'search', 'tx', edit=1, placeholder='поиск', kbEnter='search', skipEnter=1,
                **style(width=150, maxHeight=35, overflow='hidden', margin='0 2px')),
            _btnD('►', 'search', className='_', title='искать (Enter) '),
    ]


def _btn1(letter, cmd, right=None, left=None, title=''):
    styl = None
    if right:
        styl = dict(right=right)
    if left:
        styl = dict(left=left)

    return _btnD(letter, cmd, title=title, className='mBtn fv1', style=styl)


def _btn2(letter, cmd, param, right=None, left=None, title='', yes='', name=None):
    styl = None
    yes = yes and 'fv2yes'
    if right:
        styl = dict(right=right)
    if left:
        styl = dict(left=left)

    return _btnD(letter, cmd, param, name=name, title=title, className=f'mBtn2 fv2 {yes}', style=styl)


def _btnNew(dbAlias='', style=None, cmd=None, name=None):
    style = (style and dict(style)) or {}
    return _btnD(
        '', cmd or 'cmdNew', dbAlias, className=' ', style=style, name=name,
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
    return _btnD('\xa0', cmd, pk, title='просмотр', className='btnIcon btnView')


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


def _ul(tx='', **kv):
    if '\n' in tx:
        ls = tx.split('\n')
        return _teg('ul', ls[0], children=[_teg('li', x) for x in ls[1:]], **kv)
    return _teg('ul', tx, **kv)


def _ol(tx=None, **kv):
    if '\n' in tx:
        ls = tx.split('\n')
        return _teg('ol', ls[0], children=[_teg('li', x) for x in ls[1:]], **kv)
    return _teg('ol', tx, **kv)


def _li(tx=None, **kv): return _teg('li', tx, **kv)


def _a(tx=None, **kv): return _teg('a', tx, **kv)


def _lc(text, **p):
    return _teg('div', text, className='lc', **p)


def _teg(teg, text=None, **kv):
    if kv.get('skip'):
        return

    tg = {'_teg': teg}
    atr = {}
    fpr = {}
    if text:
        tg['text'] = text
    for k, v in kv.items():
        if v:
            if k == 'children':
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


def btnSvg(cmd, param, wh, r, d, **kv):
    atr = {}
    for k, v in kv.items():
        if v:
            atr[k] = v
    atr['style'] = atr.get('style', {'width': wh})

    fieldProps = {'btnD': 1, '_cmd': cmd, 'param': param} if cmd else None

    return dict(_teg='div', children=[
            _teg('svg', width=wh, height=wh, viewBox=f"0 0 {wh} {wh}", children=[
                _teg('circle', cx=f'{wh/2}', cy=f'{wh/2}', r=r, fill="#fff", stroke="#ccc", strokeWidth=1),
                _teg('path', d=d, stroke="#666", strokeWidth=2, fill="none", strokeLinecap="round")
            ])
        ], fieldProps=fieldProps, attributes=atr)


def _btnR30(cmd, param=None, **kv):
    if not kv.get('skip'):
        return btnSvg(cmd, param, 30, 15, 'M11 7 L22 15 L11 23', **kv)


def _btnL30(cmd, param=None, **kv):
    if not kv.get('skip'):
        return btnSvg(cmd, param, 30, 15, 'M19 7 L9 15 L19 23', **kv)


def _btnL40(cmd, param=None, **kv):
    if not kv.get('skip'):
        return btnSvg(cmd, param, 40, 18, 'M24 12 L14 20 L24 28', **kv)


def _btnR40(cmd, param=None, **kv):
    if not kv.get('skip'):
        return btnSvg(cmd, param, 40, 18, 'M16 12 L26 20 L16 28', **kv)


def _btnD(*p, **kv):
    if kv.get('skip'):
        return

    tg = {'_teg': 'div', 'text': p[0]}
    tg['fieldProps'] = {'btnD': 1}
    if len(p) > 1:
        tg['fieldProps']['_cmd'] = p[1]
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
        atr['className'] = atr.get('className', 'rsvTop')
        tg['attributes'] = atr
    else:
        tg['attributes'] = {'className': 'rsvTop'}
    return tg


def _button(*p, **kv):
    tg = {'_teg': 'button', 'text': p[0]}
    if len(p) > 1:
        tg['fieldProps'] = {'_cmd': p[1]}
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
    return {'_teg': 'img', 'attributes': {**attr}}


def _h2(tx, **attr):
    return _teg('h2', tx, **attr)


def _h3(tx, **attr):
    return _teg('h3', tx, **attr)


def _br():
    return {'_teg': 'br'}


def _table(*tables, rowStyle=None, skip=None):  # создает несколько таблиц
    if skip:
        return None

    ls = []  # список таблиц
    for t in tables:
        tabl = dict(r=[], rowStyle=None)  # создаем таблиц, где r-ряды, rowStyle-ее стиль
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

    ls = []  # список tr
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


def gridStyleRows(s, **kv):
    return {'style': dict(display='grid', gridTemplateRows=s, **kv)}


def labeldc(lab=None, **kv):
    att = dict(className='labeldc')
    for k, v in kv.items():
        att[k] = v
    return _div(lab or '\xa0', **att)


def label(lab=None, **kv):
    att = dict(className='label')
    for k, v in kv.items():
        att[k] = v
    return _div(lab or '\xa0', **att)


def label_(lab=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'label_ label'
    return label(lab, **atr)


def labell(lab=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'labell label'
    return label(lab, **atr)


def labelc(lab=None, **kv):
    atr = dict(**kv)
    atr['className'] = 'labelc label'
    return label(lab, **atr)


def _lf(lab, *p, **pp):
    if pp.get('skip'):
        return None
    return _div(children=[labell(lab), _field(*p, **pp)])


def labField(lab, fname, ftype='tx', flab=None, **par):
    if par.get('skip'):
        return None
    return [label(lab, name=par.get('name')), _lbf(fname, ftype, flab, **par)]


def labField_(lab, fname, ftype='tx', flab=None, **par):
    if par.get('skip'):
        return None
    return [label_(lab, name=par.get('name')), _lbf(fname, ftype, flab, **par)]


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
    return None if dp.get('skip') else _lbf(*p, **dp)


def _fileShow(fname, **kv):
    return _field(fname, 'fileShow', **kv)

# *** *** ***


def _tabNew(xName, tabs, center=None):
    '''
    tabs: [ [label or url_icon, body_div, label-width, title-icon], ...]
    in js add:

        for (let i=0; i < 10; i++)
            window.sovaActions.<form>.hide[`<xName>_${i}`] = doc => i !== doc.getField(`<xName>`);
    '''

    header = []
    body = []
    i = 0
    for it in tabs:
        if it:
            hStr, bodyIt, wit = it[:3]
            if bodyIt:
                title = it[3] if len(it) > 3 else None
                if '/' in hStr:  # url for icon
                    icon = _div(**style(padding=1, width=wit + 10), children=[
                        _div(title=title, **style(height=wit, background=f'center / contain  no-repeat url("{hStr}")'))
                    ])
                    header.append(icon)
                else:  # text
                    header.append(f'{hStr}:{wit}')
                body.append(_div(name=f'{xName}_{i}', children=[bodyIt]))
                i += 1
    grisStr = '1fr auto 1fr' if center else 'auto 1fr'
    return _div(
                className='tabNew',
                children=[
                    _div(
                        **gridStyle(grisStr),
                        children=[
                            _div(className='tnLast') if center else None,
                            _field(xName, 'band', header, **style(width='auto'), className='tnBand'),
                            _div(className='tnLast')
                        ]),
                    _div(className='tnBody', children=body)
                ])


def _tabNewSber(xName, tabs, size):
    '''
    tabs: [ [label or url_icon, body_div, label-width, title-icon], ...]
    in js add:

        for (let i=0; i < 10; i++)
            window.sovaActions.<form>.hide[`<xName>_${i}`] = doc => i !== doc.getField(`<xName>`);
    '''

    header = []
    body = []
    i = 0
    headerWidth = 0
    for it in tabs:
        if it:
            hStr, bodyIt, title = it[:3]
            if bodyIt:
                headerWidth += size + 10
                icon = _div(**style(height=size + 10, width=size), children=[
                    _div(**style(height=size, backgroundSize='100% 100%', backgroundImage=f'url("{hStr}")')),
                    _div(title),
                ])
                header.append(icon)
                body.append(_div(name=f'{xName}_{i}', children=[bodyIt]))
                i += 1

    return _div(
                className='tabNew',
                children=[
                    _field(xName, 'band', header, **style(width=headerWidth), className='tnBandSber'),
                    _div(className='tnBodySber', children=body),
                ])

# *** *** ***


def _icon(i, url, title, w=50):
    return _btnD('', f'cmdTab_{i}', **style(padding=1, width=w + 10), children=[
        _div(title=title, **style(height=w, background=f'center / contain  no-repeat url("{url}")'))
    ])

