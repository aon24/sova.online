'''
Created on 2025

@author: aon24
'''

from arm.tools.DC import well
from arm.api.forms.formTools import _img, _btnD, _btnEdit, _field, style, _div, \
    labelc, gridStyle, _tabNewSber, _btnDel, _btnView, _teg
from arm.api.forms.lk_tools import scaleEtc, manuals, contacts, \
    getSessStByProfId, btnProfile, sstFiler
from arm.api.forms.sstButtons import sstButtons

from datetime import datetime, timedelta

# *** *** ***

filterBtn = _btnD('▼ Фильтр ▼', 'showFilter', **style(right=0), itle='Фильтр', className='filterBtn')
filterGrBtn = _field('showFilterGr', 'chb', ['▼ Скрыть ▼', '▼ Группы ▼'], chbView='change', **style(left=0,), title='Показать группы', className='filterBtn')

review = _div(**style(width=150, background='#fff', margin='auto', border='2px solid #eee'), children=[
    _div('Отчеты', className='htmlHelp', **style(border='none')),
    _div(**style(display='flex', justifyContent='center', gap=10), children=[
        _div(btnD=1, _cmd='reportGr', className='reportBtn', children=[  # иконки отчетов
                _img(src='/image/bands/report-1.png'),
                _div('Группа'),
            ]),
        _div(btnD=1, _cmd='reportSt', className='reportBtn', children=[  # иконки отчетов
                _img(src='/image/bands/report-2.png'),  # , _div(), 'Контакты'),
                _div('Студент'),
            ]),
    ])
])


def showLKCurator(arm):
    '''
    Главное окна куратора
    вызывается только из арм и только для куратора-препода-сотрудника
    "для куратора отдельная форма"
    '''

    LK = _div(**style(height='100%', overflowY='auto', position='relative'), children=[
            _div(**style(display='flex', margin=5, justifyContent='center', paddingTop=5), children=[btnProfile]),
            _btnD('Выйти', 'exitLK', className='exit', title='Logoff'),  # ➡️⇒

            review,

            scaleEtc,
            _teg('hr'),
            _div(**style(textAlign='center', margin='10px 0 15px 0'), children=[
                _field('payments', 'chb', ['Платежи ▼', 'Платежи ►'],
                       className='chbChange', title='сложить/показать', chbView='change'),
            ]),
            _field('paymentsList', 'json', name='paymentsList',
                   **style(border='1px solid #ccc')),
            manuals,
        ])

    return _div(className='page51', children=[
        _div(**style(maxWidth=1200, margin='auto', height='100%', display='grid', gridTemplateRows='auto'),
             id='lk_curator',  # чтобы в js отличать
             children=[
                _div(**style(overflow='hidden'),
                     children=[
                        _tabNewSber('lks_Table_FD', [  # сверху 3 иконки Расписание-LK-Контакты
                                ('/image/bands/scheduling.png', curatorSheet(arm), 'Расписание'),
                                ('/image/bands/lk.png', LK, 'ЛК'),
                                ('/image/bands/owl.png', contacts, 'Контакты'),
                            ], 60)
                    ]
                )
            ])
        ]
    )

# *** *** ***


def curatorSheet(self):
    # Curator
    divUL1 = _div(name='groupBtnC', **style(display='inline-block', width=130), children=[
        labelc('Расписание', **style(marginTop=0)),
        _field('groupC', 'band', [], className='newBand',
               recalcText=1, rowLength=1, noRecalc=1,
               **style(width=120, textAlign='center')),  # список групп
    ])

    divUL2 = _div(name='groupBtnC', **style(display='inline-block', width=130), children=[
        labelc('Список сессий'),
        _field('groupCforOpen', 'band', [], className='newBandRed',
               noRecalc=1, recalcText=1, rowLength=1, noAlias=1,
               **style(width=120, textAlign='center')),  # it is buttons
    ])

    divUL3 = _div(name='groupBtnL', **style(display='inline-block', width=130, background='#ffc'), children=[
        labelc('Преподаватель', **style(marginTop=0)),
        _field('groupL', 'band', [], className='newBand',
               recalcText=1, rowLength=1, noRecalc=1,
               **style(width=120, textAlign='center')),  # список групп
    ])

    divUL4 = _div(name='groupBtnS', **style(display='inline-block', width=130, background='#eee'), children=[
        labelc('Сотрудник', **style(marginTop=0)),
        _field('groupS', 'band', [], className='newBand',
               recalcText=1, rowLength=1, noRecalc=1,
               **style(width=120, textAlign='center')),  # список групп
    ])

    if 0 or self._userAgent == 'mobile':
        self.leftWidth = 0
        self.leftList = None

        # self.upField = _div(**gridStyle('140px 2px 140px', margin='auto', background='#fff'), children=[
        self.upField = _div(**style(margin='auto', background='#fff'), children=[
            filterGrBtn,
            filterBtn,
            _div(name='filterGrBtn', **gridStyle('auto auto', placeItems='center center', width=260, margin='auto', textAlign='center'), children=[
                divUL1,
                divUL2,
                divUL3,
                divUL4,
            ])
        ])
    else:
        self.leftWidth = 130
        self.upField = filterBtn

        self.leftList = _div(children=[
            divUL1,
            _div('* * *', name='groupBtnC', **style(display='inline-block', textAlign='center', minWidth=130)),
            divUL2,
            divUL3,
            divUL4,
        ])

    self.viewbar = self.makeViewbar(
        **gridStyle('1px 1fr', placeItems='center center', border='none', background='transparent'),
        rightBtn=[_field('changeViewCL', 'band', ['календ|k1', 'событ|e', 'спис|l'],  # , 'к2|k2'
                         recalcText=1, className='radioBandNew', title='календарь/эскизы/список', name='lkNew')],
    )

    url = 'form=arm&cmd=showCL&view=l\
&groupC={groupC}&groupL={groupL}&groupS={groupS}\
&choosing={choosing}\
&FILTERPLANCL={FILTERPLANCL}\
&FILTEREVENTCL={FILTEREVENTCL}\
&FILTERALLOWCL={FILTERALLOWCL}'

    self.mainList = _div(**style(height='100%'), children=[
        _field('mainListCL', 'view', name='mainListCL', limit=100000, url=url, noMount=1),
        _field('showCourseCL', 'json', **style(height='100%', background='#88440020'), name='showCL')
    ])
    return self.sham()

# *** *** ***


def getViewCL(dcUK):
    mainDocs = []
    if dcUK.choosing in ['All', 'C']:
        mainDocs = getCuratorList(dcUK, dcUK.groupC)

    if dcUK.choosing in ['All', 'L']:
        mainDocs += getCuratorList(dcUK, dcUK.groupL, 'L')

    if dcUK.choosing in ['All', 'S']:
        mainDocs += getWorkerList(dcUK)

    mainDocs = [[x[0], x[1]] for x in sorted(mainDocs, key=lambda x: x[2])]

    return {'mainDocs': mainDocs, 'refsDocs': None}


def getCuratorList(dcUK, group, lector=''):
    mainDocs = []
    sgrLs = []
    for grId in group.split('-'):
        sgrLs += well('sessionsGr_GrId', grId)

    sgrLs.sort(key=lambda dc: dc.title)
    lastDay = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # скрыть прошедшие
    for sgr in sgrLs:
        if lector and dcUK.fullName not in sgr.lector:
            continue

        if not sstFiler(None, sgr, dcUK, lastDay):
            continue

        d1 = sgr.D('date_begin') or '--.--.--'
        d2 = sgr.D('date_end') or '--.--.--'

        pk = sgr.id

        sTmpl = well('sessionTmpl_id', sgr.sessionTmpl_id)
        grTitle = well('groups_groupId', sgr.nvGroup_id).title

        title = _div(f"{sTmpl.title}\nс {d1} по {d2}",
                     className='mCell', s2=1, br=1,
                     **style(width='100%', letterSpacing=1, textAlign='left'))

        if lector:  # lector
            row = _div(**gridStyle('1fr auto auto', background='#e0ffe8', placeItems='center start'),
                       children=[
                            title,
                            _btnView('cmdRead', f'unid={pk}&dbAlias=nv_SessionGr&title={grTitle}')])
        else:  # curator
            row = _div(**gridStyle('1fr auto auto', placeItems='center start'),
                       children=[
                            title,
                            _btnEdit('cmdEdit', f'unid={pk}&dbAlias=nv_SessionGr&title={grTitle}'),
                            _btnDel('deleteSessionGr', f'{pk}|\n{grTitle} ({sgr.d2})\n{sgr.Title}')
                        ])

        mainDocs.append([f'{lector}{pk}', row, sgr.date_begin])

    return mainDocs

# *** *** ***


def getWorkerList(dcUK):  # lk_student.getViewStudent
    sessStArr = getSessStByProfId(dcUK)
    mainDocs = []
    for sst in sessStArr:
        if sst.form == 'SessionGr':
            sgr = sst
            color = '#55f'
            s = 'Общая группа'
        else:
            sgr = well('sessionGr_Id', sst.SESSIONGR_ID)
            if sst.other_group:
                color = '#888'
                s = f"(подмена в {well('groups_groupId', sst.other_group).title})"
            elif sst.owner:
                color = '#f55'
                s = f"(подмена из {well('groups_groupId', sst.owner).title})"
            else:
                color = '#000'
                s = ''

        grTitle = well('groups_groupId', sgr.nvgroup_id).title
        title = _div(f"{sgr.title} ({grTitle})\n{sgr.d2}({sgr.duration}) {s}",
                     s2=1, br=1, **style(letterSpacing=1, paddingLeft=2, color=color))

        pk = f"unid={sst.id}&form={sst.form}&dbAlias=nv_{sst.form}"

        arr1 = sstButtons(sst, sgr)[0:]
        if sst.allow_s and sst.form == 'SessionSt':  # есть допуск и не 'Общая группа'
            arr2 = arr1[-2:] + [_btnEdit('cmdEdit3', pk)]  # Btn: Консультант/Эссе-OC-Редактировать
        else:
            arr2 = arr1[-2:] + [_div('\xa0', className='btnEmpty')]  # Btn: Консультант/Эссе-OC
        arr1 = arr1[:-2]  # Btn: Оплата-Допуск-Был
        d1 = _div(**style(marginTop=5), children=[_div(**gridStyle('auto auto auto'), children=arr1)])
        d2 = _div(**style(margin='5px 0'), children=[_div(**gridStyle('auto auto auto'), children=arr2)])
        row = _div(**gridStyle('1fr auto', background='#e0e8ff', placeItems='center start', maxWidth='100%'),
                   children=[title, _div(children=[d1, d2])])

        mainDocs.append([f'S{pk}', row, sgr.date_begin])

    return mainDocs

# *** *** ***
