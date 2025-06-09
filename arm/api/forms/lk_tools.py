'''
Created on 2024

@author: aon24
'''
from arm.api.forms.formTools import style, _div, _btnD, _tabNew, labField, _span, gridStyle, _field
from arm.tools.DC import DC, well, swell

# from nv.models import SessionTmpl, SessionGr

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# *** *** ***

WIDTH = 1200


def sstButtons(sst, sgr):
    if sst.pay_s:
        pay_s = ' fv2yes'
    else:
        pay_s = ''
        
        if sst.form == 'SessionGr':
            return _div('информация', **style(width=120), className=f'btnIcon mBtn fv2 fv2yes', title='общая группа'),

        begin = sgr.DATE_BEGIN  # only year-mounth
        for pay in well('payments_profile', sst.pref):
            if pay.sstId == sst.id and pay.SUMMA:
                pay_s = ' fv2yes'
                break
            elif pay.t1 == begin and pay.SUMMA:
                pay_s = ' fv2yes'
                break

    if any([1 for x in sst.keys() if x.startswith('ASSLEC')]):
        bf = ' fv2yes'
    else:
        bf = ''

    return [
        _div('Д', className=f'btnIcon mBtn fv2{sst.allow_s and " fv2yes"}', title='допущен'),
        _div('З', className=f'btnIcon mBtn fv2{sst.test_s and " fv2yes"}', title='зачет'),
        _div('Р', className=f'btnIcon mBtn fv2{pay_s}', title='оплачено'),
        _div('V', className=f'btnIcon mBtn fv2{sst.video_s and " fv2yes"}', title='видео'),
        _div('ОС', className=f'btnIcon mBtn fv2{bf}', title='обратная связь'),
    ]


def showCourse(dcUK):
    '''
    вызывается только из v_content для показа SessionTmpl в виде эскизов
    '''
    theArr = []
    nveTitle, _, nve = dcUK.nve.partition('|')
    for sesTml in well('sessionTmpl_nve', nve):
        if dcUK.status == '0':  # кнопка работе
            if sesTml['status'] != 'active':
                continue
        else:
            if sesTml['status'] == 'active':
                continue

        if dcUK.lector != 'Все' and dcUK.lector not in sesTml.lector:
            continue

<<<<<<< HEAD
        theArr.append(makeSketch(btnCmd='cmdEdit', btnPar=sesTml.id, sticker=getSticker(sesTml), title=sesTml.title))
=======
        theArr.append(makeSketch(btnCmd='cmdEdit', btnPar=sesTml.id, sticker=getSticker(sesTml), title=sesTml.title, contextMenuCmdList=None))
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

    theArr.insert(0, _div(nveTitle, className='h2', **style(color='#00f', textDecoration='none')))
    return _div(**style(width='auto', background='#00ff0010', height='100%', overflowY='auto'), children=theArr)

# *** *** ***


MONTHS = 'S Январь Февраль Март Апрель Май Июнь Июль Август Сентябрь Октябрь Ноябрь Декабрь'.split(' ')
DAYS = [_div(it, className='c_day_name' if i < 5 else 'c_day_name_wknd') for i, it in enumerate('пн вт ср чт пт сб вс'.split(' '))]


def makeSketch(btnCmd, btnPar, sticker, title, d2=None, ls=None, bg=None, contextMenuCmdList=None, disable=None):
    sh = 5
    if disable:
        btnCmd = 'disable'
        bod = _div(className='c_disabled',
            children=[
                _div(title, br=1),
        ])
    else:
        bod = _div(
            **style(borderRadius=15,
            backgroundRepeat='no-repeat', backgroundImage=sticker, backgroundSize='100% 100%'),
            children=[
                _div(title, br=1, **style(
                    color='#ffffff',
                    textShadow=f'5px 0px {sh}px #0000ff80, -5px -0px {sh}px #0000ff80, 0px 5px {sh}px #0000ff, -0px -5px {sh}px #0000ff',
                    height='100%', padding=15, overflow='hidden')
                ),
        ])
    return _div(**style(display='inline-block', margin=10, position='relative'), contextMenuCmdList=contextMenuCmdList, children=[
        _btnD('', btnCmd, btnPar,
            **style(borderRadius=15, width=190,
                display='grid', gridTemplateRows='134px 1em'),
            className='sticker',
            children=[
                bod,
                d2 and _div(d2, **style(background='#fff', textAlign='center', color='#888', margin='auto', width=170)),
                ls and _div(**style(padding='3px 0', display='flex', justifyContent='center'), children=ls),
                bg and _div(**style(height='100%', borderRadius=15,
                                    display='block', position='absolute', inset=0,
                                    border=f'2px solid #f0f0f0',
                                    background='linear-gradient(0deg, #ffFFffaa, #aaaaaa60, #ffFFffaa)')
                        )
                                    # background=bg)
        ])
    ])

# *** *** ***


def getSticker(sesTmpl):
    sticker = sesTmpl['sticker'] or well('stickerByCode', sesTmpl.nvEvent) or '/image/owl-xx.jpg'
    return f"url('{sticker}')"

# *** *** ***


def showCC(dcUK):  # календарь
    curator = lector = None
    if dcUK.cmd == 'showC3':  # studen
        sessionsGr_GrId, lsgr = getSessStByProfId(dcUK)
        addC = '3'
    else:
        sessionsGr_GrId, lsgr = getSessionsGr_GrId(dcUK)
        # lsgr - список pk групп [65,63] для "все", else [65]
        if dcUK.cmd == 'showC2':  # lector
            lector = True
            addC = '2'
        else:
            curator = True
            addC = ''

    busyDays = {}
    grTitles = {}

    for sgr in sessionsGr_GrId:
        # loadWell.loadSessionGr: dc.nvEvent = stmpl.nvEvent, dc.title = stmpl.title
        if not dcUK.event or sgr.nvEvent == dcUK.event:  # не показывать в расписании, потому что в дате нет смысла
            dbg = sgr.date_begin
            if dbg:
                busyDays[dbg] = sgr
                grTitles[dbg] = grTitles.get(dbg, [])
                if sgr.nvgroup_id:
                    gr = well('groups_groupId', sgr.nvgroup_id)
                    grTit = gr.title
                else:
                    grTit = 'Error. Not group-id'
                grTitles[dbg].append(grTit)
                if sgr.date_end and dbg < sgr.date_end:
                    while dbg < sgr.date_end:
                        dbg = datetime.strptime(dbg, "%Y-%m-%d").date() + timedelta(days=1)
                        dbg = str(dbg)
                        busyDays[dbg] = sgr
                        grTitles[dbg] = grTitles.get(dbg, [])
                        grTitles[dbg].append(grTit)

    firstDayOfMonth = []
    curMonth = []
    weeks = []
    shiftMonth = int(dcUK.shiftMonth or 0)
        
    if dcUK.dateZ:
        try:
            d = datetime.strptime(dcUK.dateZ, '%Y-%m-%d')
        except:
            d = datetime.now()
    else:
        d = datetime.now()
    dateZ = d + relativedelta(months=shiftMonth)

    for mo in range(6):  # 6 месяцев
        weeks.append([])
        current_date = (dateZ + relativedelta(months=mo)).date()
        firstDayOfMonth.append(current_date.replace(day=1))

        curMonth.append(firstDayOfMonth[mo].month)
        for we in range(6):  # в месяце м.б. 6 недель
            days = []
            for da in range(7):  # 7 дней в недели
                shift = firstDayOfMonth[mo].weekday()
                try:
                    dt = None
                    dt = datetime(firstDayOfMonth[mo].year, curMonth[mo], 1 - shift + we * 7 + da).date()
                except:
                    days.append(_div('\xa0', className='c_empty'))
                if dt:
                    cls = 'c_day-1m c_day_wknd' if da > 4 else 'c_day-1m'
                    title = None
                    if dt == datetime.now().date():
                        cls += ' c_today'
                    dts = str(dt)
                    cmd = par = contextMenuCmdList = None
                    if dts in busyDays:  # open/edit sgr
                        grt = grTitles[dts]  # grTitles[2025-11-27: [titleSes1, titleSess2...]]
                        sgr = busyDays[dts]
                        if len(lsgr) < 2:  # одна группа в этот день
                            clsEv = f' c_dayx{sgr.nvEvent}'
                            title = _div(sgr.title)
                            if curator:
                                cmd, par = 'dayX', f'unid={sgr.id}&title={grt[0]}'
                                s = f'deleteSessionGr|{sgr.id}|\n{grt[0]} ({sgr.d2})\n{sgr.title}'
                                contextMenuCmdList = [
                                    f'Редактировать|editSessionGr|{sgr.id}|{grt[0]}',
                                    f'Удалить|{s}',
                                    '',
                                ]
                                for s in swell('contextMenuCmdListSgr'):
                                    contextMenuCmdList.append(s % (lsgr[0], dts))
                            elif lector:
                                cmd, par = 'cmdOpenSess', f'rsMode=read&unid={sgr.id}&dbAlias=nv_SessionGr&form=SessionGr&title={grt[0]}'
                            else:  # student
                                form = sgr.form or 'SessionSt'  # for sessionsGrCommon form='SessionGr'
                                if sgr.allow_s:
                                    cmd, par = 'cmdOpenSess', f'rsMode=edit&unid={sgr.id}&dbAlias=nv_{form}&form={form}&title={grt[0]}'
                                else:
                                    clsEv = ' c_disabledC'
                            cls += clsEv

                        else:
                            contextMenuCmdList = ['Выберите группу||']
                            cmd, par = 'selectGr', ''
                            if len(grt) == 1:
                                title = _div(f'{grt[0]}\n{sgr.title}', br=1)
                                cls += f' c_dayx{sgr.nvEvent}'
                            else:
                                title = _div('\n'.join(grt), br=1)
                                cls += f' c_dayx'
                    else:
                        if curator:
                            if len(lsgr) == 1:
                                contextMenuCmdList = []
                                for s in swell('contextMenuCmdListSgr'):
                                    contextMenuCmdList.append(s % (lsgr[0], dts))
                            else:
                                contextMenuCmdList = ['Выберите группу||']

                    if cmd:
                        days.append(_btnD(str(dt.day), cmd, par, children=[title], className=cls, contextMenuCmdList=contextMenuCmdList))
                    else:
                        days.append(_div(str(dt.day), children=[title], className=cls, contextMenuCmdList=contextMenuCmdList))

            weeks[mo].append(_div(className='week-1m', children=days))

    def getM(no):
        s = f'{MONTHS[curMonth[no]]} {firstDayOfMonth[no].year}'
        return _div(className="month-1m", children=[
                _div(s, className="month-year-1m"),
                _div(className="week-1m-header", children=DAYS),
                _div(className="weeks-1m", children=weeks[no]),
            ])

    if dcUK.view == '0':
        return _div(className="calendar-1m", children=[
            *[getM(i) for i in range(6)],
            _btnD('◄', f'cmdMminus{addC}', className="c_arr c_left_arr"),
            _btnD('►', f'cmdMplus{addC}', className="c_arr c_right_arr"),
            _div(str(dateZ.date()), id=dcUK.dateZ_id, **style(display='none')),
        ])
    # *
    if dcUK.view == '1':
        dv = _div(**style(background='#036', margin=3, width=1))

        return _div(className='calendar-1m', children=[
                _div(**style(display='grid', gridTemplateColumns='1fr 7px 1fr', height='100%'), children=[getM(0), dv, getM(1)]),
                _div(**style(display='grid', gridTemplateColumns='1fr 7px 1fr', height='100%'), children=[getM(2), dv, getM(3)]),
                _div(**style(display='grid', gridTemplateColumns='1fr 7px 1fr', height='100%'), children=[getM(4), dv, getM(5)]),
            _btnD('◄', f'cmdMminus{addC}', className="c_arr c_left_arr"),
            _btnD('►', f'cmdMplus{addC}', className="c_arr c_right_arr"),
            _div(str(dateZ.date()), id=dcUK.dateZ_id, **style(display='none')),
        ])

    # ***


def getSessionsGr_GrId(dcUK):
    '''
    dcUK.selected   # Все группы|65-60 or 2022-6/Дн|65
    status: 0-inWork, 1-closed
    '''
    titleGr, _, ls = dcUK.selected.partition('|')
    lsgr = ls.split('-')
    ls = []
    for gr in lsgr:
        for sgr in well('sessionsGr_GrId', gr):  # dc-sgr + stmpl.title + stmpl.event
            if not sgr['d2'] and titleGr == 'Все группы':  # расписание
                continue

            if dcUK.status == '0' and sgr['status'] != 'active':  # кнопка работе
                continue

            if dcUK.cmd == 'showC2' and not sgr.commonGroups:  # lector
                if dcUK.showLK_id:  # from sheet 'office'
                    lector = well('profiles', dcUK.showLK_id)
                    if not (lector and lector.full_name in sgr.lector):
                        continue

                elif dcUK.fullName not in sgr.lector:
                    continue

            ls.append(sgr)

    return sorted(ls, key=lambda x: x.date_begin), lsgr


def showC(dcUK):  # эскизы
    # вызываается из
    # 1. arm: студента(cmd=showC3)/куратора/lector
    # 2. v_shedule - расписание(cmd=getSelected&plan=1&view=2&selected=2024-2/DN|46&status=0&upList=0&event=

    days = 1 if dcUK.plan == '0' else 100000
    yesterday = datetime.now() - timedelta(days=days)
    last = yesterday.strftime("%Y-%m-%d")

    if dcUK.cmd == 'showC3':
        curator = None
        sessArr, lsgr = getSessStByProfId(dcUK)
        titleGr = 'Расписание'
    else:
        curator = dcUK.cmd != 'showC2'  # not lector
        sessArr, lsgr = getSessionsGr_GrId(dcUK)
        titleGr = f"Расписание ({dcUK.selected.partition('|')[0]})"  # Все группы|65-60

    byEvent = {titleGr: [], well('eventsByCode', 'CL'): []}

    for sgr in sessArr:  # dc-sgr + stmpl.title + stmpl.nvEvent
        dateEnd = sgr.date_end or sgr.date_begin
        if dcUK.cmd != 'showC3':  # NU 08-jun показать все с допуском или вообще все, но без д. серыми
            if dateEnd < last:  # не показ эскизы через 1 день после оконч or isEmpty
                continue

        if sgr.nvEvent == 'CL':
            event = well('eventsByCode', 'CL')
        else:
            event = titleGr

        if dcUK.cmd == 'showC3':  # sgr м.б. sst, а может быть sgr
            if sgr.form == 'SessionGr':  # for sessionsGrCommon form='SessionGr'
                form = 'SessionGr'
                sgr2 = sgr
                disable = None
            else:
                form = 'SessionSt'
                sgr2 = well('sessionGr_Id', sgr.SESSIONGR_ID)
                disable = not sgr.ALLOW_S
            edc = dict(form=form, pk=sgr.id, d2=sgr.d2, title=sgr.title, sticker=sgr.sticker, ls=sstButtons(sgr, sgr2), disable=disable)
        else:
            stmpl = well('sessionTmpl_id', sgr.sessionTmpl_id)
            sticker = getSticker(stmpl)
            edc = dict(pk=sgr.id, nvgroup=sgr.nvgroup_id, d2=sgr.d2, title=sgr.title, sticker=sticker)

        byEvent[event].append(edc)

    smArr = []
    for k in byEvent:
        theArr = []
        for ss in byEvent[k]:
            if dcUK.cmd == 'showC3':
                btnCmd = 'cmdOpenSess'
                btnPar = f"form={ss['form']}&rsMode=edit&dbAlias=nv_{ss['form']}&unid={ss['id']}&title={ss['title']}"

                theArr.append(makeSketch(
                    btnCmd=btnCmd,
                    btnPar=btnPar,
                    sticker=ss['sticker'],
                    title=ss['title'],
                    d2=ss['d2'],
                    ls=ss['ls'],
                    disable=ss.get('disable')
                ))
                continue

            group = well('groups_groupId', ss['nvgroup']).title

            if len(lsgr) == 1:
                title = ss["title"]
            else:
                title = f'{group}\n{ss["title"]}'

            if curator:
                btnCmd, btnPar = 'dayX', f'unid={ss["pk"]}&title={group}'
                s = f'deleteSessionGr|{ss["pk"]}|\n{group} ({ss["d2"]})\n{ss["title"]}'
                contextMenuCmdList = [
                    f'Редактировать|editSessionGr|{ss["pk"]}|{group}',
                    f'Удалить|{s}',
                ]
            else:
                contextMenuCmdList = None
                btnCmd = 'cmdOpenSess'
                btnPar = f'rsMode=read&unid={ss["pk"]}&title={ss["title"]}&dbAlias=nv_SessionGr'

            theArr.append(makeSketch(
                btnCmd=btnCmd,
                btnPar=btnPar,
                sticker=ss['sticker'],
                title=title,
                d2=ss['d2'],
                contextMenuCmdList=contextMenuCmdList,
            ))

        if theArr:
            sm = _div(k, className='h3', **style(background='#44ff8810', padding=10,), children=[
                _div(children=theArr, **style(font='700 14px Verdana,Arial', color='#036', textAlign='center'))
            ])

            smArr.append(sm)

    smArr.insert(0, _div(swell('programm')[0], className='h2', **style(color='#00f', textDecoration='none')))

    return _div(**style(width='auto', background='#ff000010', height='100%', overflowY='auto'), children=smArr)

# *** *** ***


btnLogout = _btnD('🔚', 'logout', className='propBtn', **style(left=0))
btnSetting = _btnD('🛠️', 'previewArm', 'newForm=etc&title=Настройки&dbAlias=etc', className='propBtn', **style(right=0))
btnProfile = _field('openProfile', 'btn', fd=1)


def showLKphone(table, fioCLS=None):
    if fioCLS:  # for office-mode
        fio, _, pk = fioCLS.partition('|')
        fioCLS = _btnD(fio, 'openProfile2', pk, **style(font='bold 12px Arial', color='#036'))

    return _div(
        className='page51',
        children=[
            btnLogout,
            btnSetting,
            _div(**style(maxWidth=WIDTH, margin='auto'),
                children=[
                    _div(className='propfile', children=[
                        btnProfile,
                        fioCLS
                    ]),
                    _div(**style(overflow='hidden', height='calc(100vh - 32px)'),
                        children=[_tabNew('LK_Table_FD', tabs=table)]
                    )
            ])
    ])

# *** *** ***


def armButtom(su):
    btn = [
        _btnD('Пользователи', 'previewArm', 'newForm=v_profiles&title=Профайлы'),
        _btnD('Программа', 'previewArm', 'newForm=v_content&title=Программа'),
        _btnD('Расписание', 'previewArm', 'newForm=v_schedule&title=Расписание'),
        _btnD('Список групп', 'previewArm', 'newForm=v_groups&title=Список групп'),
        _btnD('Студенты по гр.', 'previewArm', 'newForm=v_students&title=Студенты'),
        _btnD('Платежи', 'previewArm', 'newForm=v_payments&title=Платежи'),
        _btnD('Тр-Фест-Озн.сем', 'previewArm', 'newForm=v_invite&title=Тренинг Фест Озн.сем.'),
        _btnD('Справочники', 'previewArm', 'newForm=v_classifiers&title=Справочники'),
        _btnD('О Т Ч Е Т Ы', 'previewArm', 'newForm=v_reports&title=Отчеты и аналитика&rsMode=edit', **style(margin='10px 20px')),
    ]
    if su:
        btn.append(_btnD('Обр.связь', 'previewArm', 'newForm=v_reports&title=Отчеты и аналитика&rsMode=edit&addUrl:&domain=feedback', **style(margin='10px 20px')))

    return _div(className='armPcBtn', **style(background='#FFD78040'), children=btn)


def office():

    return _div(
        **style(margin='auto', padding=5, textAlign='center', height='100%', overflow='auto'),
        children=[
            _div(
                **style(width=250, margin='10px auto 0'),
                children=[
                    # label('Новый пользователь на озн. семинар'),
                    _btnD('Создать пользователя', 'newProfile', 'OS'),  # only for staff !!!
            ]),
            _div(**style(width=220, display='inline-block', margin=10, textAlign='left', verticalAlign='top'),
                children=[
                    *labField('Ознакомительный семинар', 'invite', 'lbsd', '/api/well?clues=invite', placeholder='Список'),
            ]),
            _div(**style(width=220, display='inline-block', margin=10, textAlign='left', verticalAlign='top'),
                children=[
                    *labField('Источник информации', 'info', 'lbsd', '/api/well?clues=info', placeholder='Список'),
            ]),
            _div(**style(width=150, display='inline-block', margin=10, textAlign='left', verticalAlign='top'),
                children=[
                    *labField('Роль', 'role', 'lbsd', '/api/well?clues=role', placeholder='Список'),
            ]),

            _div(**style(marginTop=15, border='0 solid #036', borderTopWidth=1)),

            # ***

            _div('Проверить личный кабинет пользователя', **style(marginTop=15), className='h3'),
            _div(
                **style(margin=10, width=300, display='inline-block', textAlign='left'),
                children=[
                    *labField('Показать ЛК сотрудника', 'showTutor', 'lbsd', '/api/well?clues=tutors2'),
            ]),
            _div(
                **style(margin=10, width=300, display='inline-block', textAlign='left'),
                children=[
                    *labField('Показать ЛК студента', 'showStudent', 'lbsd', '/api/well?clues=студент2'),
            ]),
        ])


def showLKpc(table, fioCLS=None, su=None):
    if fioCLS:
        fio, _, pk = fioCLS.partition('|')
        fioCLS = _btnD(fio, 'openProfile2', pk, **style(font='bold 14px Arial', color='#036'))
    return _div(
        className='page51',
        children=[
            btnLogout,
            btnSetting,
            _div(**style(maxWidth=WIDTH + 250, margin='auto'), children=[
                _div(className='propfile', children=[
                    btnProfile,
                    _span('  '),
                    fioCLS
                ]),
                _div(**gridStyle('170px 1fr', overflow='hidden', height='calc(100vh - 30px'),
                    children=[
                        armButtom(su),
                        _div(**style(height='inherit', padding=1),
                            children=[_tabNew('LK_Table_FD', tabs=table)]
                    )
                ]),
            ]),

    ])

# *** *** ***


def getSessStByProfId(dcUK):
    # selGrId = dcUK.group.partition('|')[2]  # group=2022-8/Дн|66
    byGroup = []
    studId = dcUK.showLK_id or dcUK._profilePK
    sstArr = list(well('sessionSt_idPr', studId) or []) + well('sessionsGrCommon')
    # !!! well('sessionsGrCommon') - здесь уже сессии общих групп

    if dcUK.event:
        events = [dcUK.event]
    else:
        events = [e.partition('|')[2] for e in swell('shortEvents')]

    for sst in sstArr:
        if sst.sessiongr_id:
            sgr = well('sessionGr_Id', sst.sessiongr_id)
        else:
            sgr = sst  # она и есть сессия группы

        if dcUK.view == '2':  # эскизы - убираем лишнее
            if sgr.nvEvent not in events:  # nvEvent - '1', ... 'CL'
                continue
        # календарь в режиме "все" показывает все(вкл Пр 1,2)
        elif dcUK.event:  # календарь не в режиме "все"
            if sgr.nvEvent not in events:
                continue

        if sgr.status != 'active':
            continue

        if dcUK.status == '0' and not sst.ALLOW_S:  # только с допуском
            continue

        stmpl = well('sessionTmpl_id', sgr.sessiontmpl_id)

        d = DC(sst)
        d.title = stmpl['title']
        d.sticker = getSticker(stmpl)
        for k in ['d2', 'date_begin', 'date_end', 'nvgroup_id', 'duration', 'nvEvent']:
            d[k] = sgr[k]

        byGroup.append(d)

    return sorted(byGroup, key=lambda dc: dc.date_begin), []


# *** *** ***


def rightBtnLK(n, userAgent, na=None):
    '''
    n = '', '2', '3' - curator, lector, student
    na = 'viewbar1' в форме v_shedule
    '''
    if userAgent == 'mobile':
        event = _field(f'event{n}', 'lbsd', list(['Все|'] + swell('events')), recalcText=1, edit=1, xValue='Все',
            title='выберите событие',
            name=f'event{n}')
    else:
        event = _field(f'event{n}', 'band', swell('shortEvents'), recalcText=1,
            className='radioBand',
            title='выберите событие',
            name=f'event{n}')

    return [
        _field(f'changeView{n}', 'band', ['к1', 'к2', 'эскиз', 'спис'], className='radioBand',
            title='календарь/эскизы/список', name=na),
        _div(**style(flex=1)),

        event,

        _field(f'plan{n}', 'band', ['Планируемые', 'все'], className='radioBand', name=f'plan{n}'),
        _div(**style(flex=1)),
        _field(f'status{n}', 'band', ['актив', 'все'], className='radioBand'),
    ]


def rightBtnLK3():
    event = _field(f'event3', 'band', swell('shortEvents'), recalcText=1,
        className='radioBand',
        title='выберите событие',
        name=f'event3+')

    return [
        _field(f'changeView3', 'band', ['к1', 'к2', 'события'], className='radioBand', title='календарь/эскизы'),
        _div(**style(flex=1)),
        event,
        _div(**style(flex=1)),
        _field(f'status3', 'band', ['допуск', 'все'], className='radioBand'),
    ]
