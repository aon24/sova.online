'''
Created on 2024

@author: aon24
'''

from arm.api.forms.formTools import _btnL40, _btnR40, _btnD, _field, style, \
    _teg, _div, gridStyle, _tabNewSber, _img
from arm.api.forms.lk_tools import scaleEtc, manuals, contacts, btnProfile

# *** *** ***


def studentTabNew(arm, center=None):
    '''
    table wi sber
    сверху 3 иконки Расписание-LK-Контакты
    внизу 3 боди
    '''
    if arm.studentOnly:
        LK = _div(**style(height='100%', overflowY='auto', position='relative'), children=[
                _div(**style(display='flex', justifyContent='center', paddingTop=5),
                     children=[btnProfile]),
                _btnD('Выйти', 'exitLK', className='exit', title='Logoff'),  # ➡️⇒

                _div(btnD=1, _cmd='reportSt3', **style(marginTop=5), className='reportBtn', children=[  # иконки отчетов
                        _img(src='/image/bands/report-2.png'),  # , _div(), 'Контакты'),
                        _div('Отчет'),
                    ]),

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
    else:
        LK = _div(**style(height='100%', overflowY='auto', position='relative'), children=[
                _div(**style(textAlign='center', margin='10px 0 15px 0'), children=[
                    _field('payments', 'chb', ['Платежи ▼', 'Платежи ►'],
                           className='chbChange', title='сложить/показать', chbView='change'),
                ]),
                _field('paymentsList', 'json', name='paymentsList',
                       **style(border='1px solid #ccc')),
            ])

    return _tabNewSber('lks_Table_FD', [
        ('/image/bands/scheduling.png', studentSheet(arm), 'Расписание'),
        ('/image/bands/lk.png', LK, 'ЛК'),
        ('/image/bands/owl.png', contacts, 'Контакты'),
    ], 60)

# *** *** ***


def showLKStudent(arm):
    '''
    Главное окна студента
    вызывается только из арм и только для студента
    "для студня отдельная форма"
    '''
    # if arm.studentNewThema:
    if arm.studentOnly:
        return _div(className='page51', children=[
                    _div(**style(maxWidth=1200, margin='auto', height='100%', position='relative'),
                         children=[
                            _btnD('▼ Ф ▼', 'showFilter', **style(right=0), title='Фильтр', name='filterBtn', className='filterBtn'),
                            _btnR40('btnR40', className='btnR40', **style(right=0), name='filterBtn'),
                            _btnL40('btnL40', className='btnR40', **style(left=0), name='filterBtn'),
                            _field('fieldR40', 'btn', xValue='эскиз|btnR40', className='btnR40',
                                   **style(font='normal 12px Verdana', right=0, padding='11px 25px 0 0', width=60, textAlign='right'),
                                   name='filterBtn'),
                            _field('fieldL40', 'btn', xValue='спис|btnL40', className='btnR40',
                                   **style(font='normal 12px Verdana', left=0, padding='11px 0 0 25px', width=60, textAlign='left'),
                                   name='filterBtn'),
                            studentTabNew(arm)
                        ])
                    ])
    else:
        return _div(className='page51', children=[
            _div(**style(maxWidth=1200, margin='auto', height='100%',
                         display='grid', gridTemplateRows='auto 1fr',
                         ),
                 children=[
                    _div(**style(overflow='hidden'),
                         children=[studentTabNew(arm)]
                         )
                    ])
                ]
            )

# *** *** ***


def office_student(arm):
    '''
    Вкладка "сотрудник" или "студент"
    center=True
    вызывается из арм в режиме "офис" для создания вкладки "сотрудник" или "студент",
    '''
    return _div(
        **style(height='100%', paddingTop=5),  # background='url("/image/nvbg.jpeg")'),
        children=[
            # _div(**style(width=250, margin='auto', boxShadow='0px 17px 5px 20px #fff')),
            studentTabNew(arm, center=True),
        ])

# *** *** ***


def studentSheet(arm):
    '''
    вкладка "Расписание"
    обеспечивает доступ к сст
    содержит календарь/эскизы/список сст
    '''

    url = 'form=arm&cmd=getEdges&view=l\
&FILTERALLOW3={FILTERALLOW3}\
&FILTERPLAN3={FILTERPLAN3}\
&FILTERWAS3={FILTERWAS3}\
&FILTERPAYMENT3={FILTERPAYMENT3}\
&FILTEREC3={FILTEREC3}\
&FILTERFEEDBACK3={FILTERFEEDBACK3}\
&FILTEREVENT3={FILTEREVENT3}'

    if arm.studentOnly:
        edges = dict(
            face=_field('calendar1m', 'json', **style(height='100%', overflow='auto')),
            right=_field('images', 'json', **style(height='100%',)),
            far=_field('calendar2m', 'json', **style(height='100%',)),
            left=_field('mainList3', 'view', limit=100000, url=url, noMount=1),
        )
        return _field('cube', 'cube', readOnly=1, xyz=['100%', '100%', 'x'], perspective=700, edges=edges)

    # ***

    arm.leftList = arm.leftWidth = arm.upField = None
    arm.viewbar = arm.makeViewbar(
        **gridStyle('1px 1fr', borderWidth='0 0 0px 0', background='transparent'),
        rightBtn=[
            _field('changeView3', 'band', ['календ|k1', 'события|e', 'спис|l'],  # , 'к2|k2'
                   recalcText=1, className='radioBandNew', title='календарь/эскизы'),
            _div(**style(flex=1)),
            _btnD('▼ Фильтры ▼', 'showFilter', title='Фильтр', className='filterBtn2'),
        ],
    )

    arm.mainList = _div(**style(height='100%'), children=[
        _field('mainList3', 'view', name='mainList3', limit=100000, url=url + '&showLK_id={showLK_id}', noMount=1),
        _field('showCourse3', 'json', **style(height='100%',), name='showCL3'),
    ])
    sh = arm.sham()

    return sh

# *** *** ***
