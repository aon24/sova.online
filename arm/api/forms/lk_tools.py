'''
Created on 2024

@author: aon24
'''
from arm.api.forms.formTools import _lc, style, _div, _btnD, _tabNew, labField, \
    gridStyle, _field, _btnR30, _btnL30
from arm.tools.DC import DC, well, swell
from arm.api.forms.sstButtons import sstButtons

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# *** *** ***

WIDTH = 1200


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

        theArr.append(makeSketch(btnCmd='cmdEdit', btnPar=sesTml.id, sticker=getSticker(sesTml), title=sesTml.title))

    theArr.insert(0, _div(nveTitle, className='h2', **style(color='#00f', textDecoration='none')))
    return _div(**style(width='auto', height='100%', overflowY='auto'), children=theArr)

# *** *** ***


MONTHS = 'S Январь Февраль Март Апрель Май Июнь Июль Август Сентябрь Октябрь Ноябрь Декабрь'.split(' ')
MONTHS2 = 'S Янв Фев Март Апр Май Июнь Июль Авг Сент Окт Нояб Дек'.split(' ')
DAYS = [_div(it, className='c_day_name' if i < 5 else 'c_day_name_wknd') for i, it in enumerate('пн вт ср чт пт сб вс'.split(' '))]
DAYS2 = [_div(it, className='c_day_name' if i < 5 else 'c_day_name_wknd') for i, it in enumerate('п в с ч п с в'.split(' '))]


def makeSketch(btnCmd, btnPar, sticker, title, d2=None, ls=None, bg=None, contextMenuCmdList=None, disable=None):
    sh = 5
    if disable:
        btnCmd = 'disable'
        bod = _div(
                className='c_disabled',
                children=[
                    _div(title, br=1),
                ])
    else:
        bod = _div(
            **style(
                borderRadius=15, backgroundRepeat='no-repeat', backgroundImage=sticker,
                backgroundSize='100% 100%'),
            children=[
                _div(
                    title, br=1,
                    **style(
                        color='#ffffff',
                        textShadow=f'5px 0px {sh}px #0000ff80, -5px -0px {sh}px #0000ff80, 0px 5px {sh}px #0000ff, -0px -5px {sh}px #0000ff',
                        height='100%', padding=15, overflow='hidden')
                ),
            ])

    return _div(**style(display='inline-block', margin=10, position='relative'), contextMenuCmdList=contextMenuCmdList, children=[
        _btnD(
            '', btnCmd, btnPar,
            **style(
                borderRadius=15, width=190,
                display='grid', gridTemplateRows='134px 1em'),
            className='sticker',
            children=[
                bod,
                d2 and _div(d2, **style(background='#fff', textAlign='center', color='#888', margin='auto', width=170)),
                ls and _div(**style(padding='3px 0', display='flex', justifyContent='center'), children=ls),
                bg and _div(**style(height='100%', borderRadius=15,
                                    display='block', position='absolute', inset=0,
                                    border='2px solid #f0f0f0',
                                    background='linear-gradient(0deg, #ffFFffaa, #aaaaaa60, #ffFFffaa)')
                            )
            ])
    ])

# *** *** ***


def getSticker(sesTmpl):
    sticker = sesTmpl['sticker'] or well('stickerByCode', sesTmpl.nvEvent) or '/image/owl-xx.jpg'
    return f"url('{sticker}')"

# *** *** ***


def showCC(dcUK):  # календарь
    '''
    Интервал задается: dateZ, dcUK.shiftMonth(1 or -1)
    dateZ = dcUK.dateZ or now:   дата (месяц), который у юзера первый на экране or now
    '''

    def makeBusyDays():
        # формирует список занятых дней и отсекает тех, кто не попал в заданный интервал.
        # loadWell.loadSessionGr добавляет поля: dc.nvEvent = stmpl.nvEvent, dc.title = stmpl.title
        for sgr in sessionsGr_GrId:
            dateBg = sgr.date_begin
            if dateBg:  # не показывать в расписании, потому что в дате нет смысла
                dateBegin = datetime.strptime(dateBg, "%Y-%m-%d").date()
                dateEnd = datetime.strptime(sgr.date_end or dateBg, "%Y-%m-%d").date()
                if dateBegin >= intervalEnd or dateEnd < intervalStart:
                    continue

                if sgr.nvgroup_id:
                    gr = well('groups_groupId', sgr.nvgroup_id)
                    sgr.grTitle = gr.title
                else:
                    sgr.grTitle = f'Error. Not group-id(sgr: {sgr.id})'

                dt = dateBegin
                while dt <= dateEnd:
                    dateBg = str(dt)
                    if dateBg in busyDays:
                        flag = False
                        for s in busyDays[dateBg]:
                            if s.id == sgr.id:  # если куратор еще и лектор, одна и та же сгр м.б. 2-3 раза
                                s.persona += '|' + sgr.persona
                                flag = True
                        if not flag:
                            busyDays[dateBg].append(sgr)
                    else:
                        busyDays[dateBg] = [sgr]
                    dt += timedelta(days=1)

        # *** *** ***

    # *** *** ***

    busyDays = {}

    # определяем интервал в 3 месяца от даты на экране
    if dcUK.dateZ:  # дата (месяц), который у юзера первый на экране
        try:
            d = datetime.strptime(dcUK.dateZ, '%Y-%m-%d')
        except Exception:
            d = datetime.now()
    else:
        d = datetime.now()
    shiftMonth = int(dcUK.shiftMonth or 0)
    dateZ = d + relativedelta(months=shiftMonth)

    intervalStart = dateZ.replace(day=1).date()
    intervalEnd = intervalStart + relativedelta(months=3)  # + 3 месяца

    # ***

    addC = ''
    curatorGroup = None
    dcUK.filterPlanCL = dcUK.filterPlan3 = ''  # календарь д. показать все

    if dcUK.cmd == 'showCL':  # studen (call from from LK-curator/lector/worker)

        if dcUK.choosing in ['All', 'C']:  # curator or all
            dcUK.persona = 'curator'
            sessionsGr_GrId = getSessionsGr_GrId(dcUK, group=dcUK.groupC)
            curatorGroup = dcUK.groupC
            makeBusyDays()

        if dcUK.choosing in ['All', 'L']:  # lector or all
            dcUK.cmd = 'showC2'  # костыль № 734
            dcUK.persona = 'lector'
            sessionsGr_GrId = getSessionsGr_GrId(dcUK, group=dcUK.groupL)
            makeBusyDays()

        if dcUK.choosing in ['All', 'S']:  # worker or all
            dcUK.persona = 'student'
            sessionsGr_GrId = getSessStByProfId(dcUK)
            makeBusyDays()
        addC = 'CL'

    elif dcUK.cmd == 'showC3':  # studen (call from office or from LK-student)
        dcUK.persona = 'student'
        sessionsGr_GrId = getSessStByProfId(dcUK)
        makeBusyDays()
        addC = '3'
    else:  # dcUK.cmd: showC or showC2(call from office)
        # lsgr - список pk групп [65,63] для "все", else [65]
        if dcUK.cmd == 'showC2':  # lector
            dcUK.persona = 'lector'
            addC = '2'
        else:
            dcUK.persona = 'curator'
            curatorGroup = dcUK.selected
        sessionsGr_GrId = getSessionsGr_GrId(dcUK, group=dcUK.selected)
        makeBusyDays()

    if not (dcUK._staff or 'куратор' in dcUK._role):
        curatorGroup = None  # запретить добавлять sst правой кнопкой на пустой клетке

    firstDayOfMonth = []
    curMonth = []
    weeks = []  # в списке 3 списка(3 месяца), в каждом из трех 6 недель

    for mo in range(3):  # 3 месяцa
        weeks.append([])
        current_date = (dateZ + relativedelta(months=mo)).date()
        firstDayOfMonth.append(current_date.replace(day=1))

        curMonth.append(firstDayOfMonth[mo].month)

        # проверяем 42 дня (6 недель по 7 дней) и, если день есть, dt = datetime
        for we in range(6):  # в месяце м.б. 6 недель
            days = []
            for da in range(7):  # 7 дней в недели
                shift = firstDayOfMonth[mo].weekday()
                try:
                    dt = datetime(firstDayOfMonth[mo].year, curMonth[mo], 1 - shift + we * 7 + da).date()
                except Exception:
                    days.append(_div('\xa0', className='c_empty'))  # пустая клетка(в месяце дней < 42)
                    continue

                cls = 'c_day-1m c_day_wknd' if da > 4 else 'c_day-1m'
                title = None
                if dt == datetime.now().date():
                    cls += ' c_today'
                dts = str(dt)
                cmd = par = contextMenuCmdList = None

                # проверяем, есть ли что-то  в этот день
                if dts in busyDays:  # open/edit sgr
                    lsSgr = busyDays[dts]
                    if len(lsSgr) == 1:  # одна сессия групп в этот день
                        sgr = lsSgr[0]
                        clsEv = f' c_dayx{sgr.nvEvent}'
                        title = _div(sgr.title)

                        if 'curator' in sgr.persona:  # краторная группа
                            cmd, par = 'dayX', f'unid={sgr.id}&title={sgr.grTitle}'
                            # s = deleteSessionGr|id|text in msgBox
                            s = f'deleteSessionGr|{sgr.id}|\n{sgr.grTitle} ({sgr.d2})\n{sgr.title}'
                            contextMenuCmdList = [
                                f'Редактировать|editSessionGr|{sgr.id}|{sgr.grTitle}',
                                f'Удалить|{s}',
                            ]
                            if '-' not in curatorGroup:  # not несколько групп
                                contextMenuCmdList.append('')  # разделитель
                                for s in swell('contextMenuCmdListSgr'):
                                    contextMenuCmdList.append(s % (sgr.nvGroup_id, dts))

                        elif 'lector' in sgr.persona:
                            cmd = 'cmdOpenSess'
                            par = f'rsMode=read&unid={sgr.id}&dbAlias=nv_SessionGr&form=SessionGr&title={sgr.grTitle}'
                        else:  # student
                            form = sgr.form or 'SessionSt'  # for sessionsGrCommon form='SessionGr'
                            if sgr.allow_s:
                                cmd, par = 'cmdOpenSess', f'rsMode=edit&unid={sgr.id}&dbAlias=nv_{form}&form={form}&title={sgr.grTitle}'
                            else:
                                clsEv = ' c_disabledC'
                        cls += clsEv

                    else:  # несколько событий или несколько групп в 1 день
                        if curatorGroup and '-' in curatorGroup:
                            contextMenuCmdList = ['Выберите группу||']
                            cmd, par = 'selectGr', ''
                        else:
                            contextMenuCmdList = ['Несколько событий в день. Используйте список или эскизы.||']
                            cmd, par = 'manyEvent', ''

                        title = _div('\n---\n'.join([sgr.title for sgr in lsSgr]), br=1)
                        cls += ' c_dayx'
                else:  # пустая клетка
                    if curatorGroup:
                        if '-' in curatorGroup:  # несколько групп
                            contextMenuCmdList = ['Выберите группу||']
                        else:
                            contextMenuCmdList = []
                            for s in swell('contextMenuCmdListSgr'):
                                contextMenuCmdList.append(s % (curatorGroup, dts))

                if cmd:
                    days.append(_btnD(str(dt.day), cmd, par, children=[title], className=cls, contextMenuCmdList=contextMenuCmdList))
                else:
                    days.append(_div(str(dt.day), children=[title], className=cls, contextMenuCmdList=contextMenuCmdList))

            weeks[mo].append(_div(className='week-1m', children=days))

    m6 = []
    if dcUK.view == 'k1':
        for no in range(3):
            monPlMi = _div(className="month-year-mi-pl", children=[
                _btnL30(f'cmdMminus{addC}'),  # ◄►
                _div(f'{MONTHS[curMonth[no]]}\xa0{firstDayOfMonth[no].year}', **style(padding='0 6px')),
                _btnR30(f'cmdMplus{addC}'),
            ])
            m6.append(_div(className="month-1m", children=[
                monPlMi,
                _div(className="week-1m-header", children=DAYS),
                _div(className="weeks-1m", children=weeks[no]),
            ]))

        return _div(className="calendar-1m", children=[
            *m6,
            _div(str(dateZ.date()), id=dcUK.dateZ_id, **style(display='none')),
        ])

    if dcUK.view == 'k2':
        for no in range(1):
            monPlMi1 = \
                _div(
                    children=[
                        _div(
                            className="month-year-mi-pl", **gridStyle('auto auto'), children=[
                                _btnL30(f'cmdMminus{addC}'),
                                _div(f'{MONTHS2[curMonth[no*2]]}\xa0{str(firstDayOfMonth[no*2].year)[-2:]}', **style(padding='0 6px')),
                            ]),
                        _div(className="week-1m-header", children=DAYS2),
                        _div(className="weeks-1m", children=weeks[no * 2]),
                        ],
                    **style(border='0 solid #036', borderRightWidth=2))
            monPlMi2 = \
                _div(children=[
                    _div(className="month-year-mi-pl", **gridStyle('auto auto'), children=[
                        _div(f'{MONTHS2[curMonth[no*2+1]]}\xa0{str(firstDayOfMonth[no*2+1].year)[-2:]}', **style(padding='0 6px')),
                        _btnR30(f'cmdMplus{addC}'),
                    ]),
                    _div(className="week-1m-header", children=DAYS2),
                    _div(className="weeks-1m", children=weeks[no * 2 + 1]),
                ])
            m6.append(
                _div(
                    **gridStyle('50% 50%', minHeight='100%'),
                    children=[monPlMi1, monPlMi2]))

        return _div(className="calendar-1m", children=[
            *m6,
            _div(str(dateZ.date()), id=dcUK.dateZ_id, **style(display='none')),
        ])

    # ***


def getSessionsGr_GrId(dcUK, group):
    '''
    group   # Все группы|65-60 or 2022-6/Дн|65
    status: 0-inWork, 1-closed
    '''
    titleGr = '-' in group and 'Все группы'

    lsgr = group.split('-')
    ls = []
    lastDay = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # скрыть прошедшие
    for gr in lsgr:
        for sgr in well('sessionsGr_GrId', gr):  # dc-sgr + stmpl.title + stmpl.event
            titleGr = titleGr or well('groups_groupId', sgr.NVGROUP_ID).title
            if not sgr.d2 and titleGr == 'Все группы':  # расписание
                continue

            if not sstFiler(None, sgr, dcUK, lastDay):
                continue

            if (dcUK.cmd == 'showC2' or dcUK.choosing == 'L') and not sgr.commonGroups:  # lector
                if dcUK.showLK_id:  # from sheet 'office'
                    lector = well('profiles', dcUK.showLK_id)
                    if not (lector and lector.full_name in sgr.lector):
                        continue

                elif dcUK.fullName not in sgr.lector:
                    continue

            sgr.persona = dcUK.persona
            ls.append(sgr)

    dcUK.titleGr = titleGr
    return sorted(ls, key=lambda x: x.date_begin)


def getSessionKit(dcUK):  # эскизы
    # вызываается из
    # 1. arm: студента (cmd=showC3)
    # 2. arm: куратора/lector/worker (cmd=showCL)
    # 3. office
    # 4. v_shedule - расписание(cmd=getSelected&plan=1&view=2&selected=2024-2/DN|46&status=0&upList=0&event=

    def iconList(titleH3):
        byEvent[titleH3] = []
        for sgr in sessArr:  # dc-sgr + stmpl.title + stmpl.nvEvent
            if persona == 'Сотрудник':  # sgr м.б. sst, а может быть sgr
                if sgr.form == 'SessionGr':  # for sessionsGrCommon form='SessionGr'
                    form = 'SessionGr'
                    sgr2 = sgr
                    disable = None
                else:
                    form = 'SessionSt'
                    sgr2 = well('sessionGr_Id', sgr.SESSIONGR_ID)
                    disable = not sgr.ALLOW_S

                edc = dict(
                    form=form,
                    pk=sgr.id,
                    d2=sgr.d2,
                    title=sgr.title,
                    sticker=sgr.sticker,
                    ls=sstButtons(sgr, sgr2),
                    disable=disable,
                    persona=persona,
                )
            else:
                stmpl = well('sessionTmpl_id', sgr.sessionTmpl_id)
                edc = dict(
                    pk=sgr.id,
                    nvgroup=sgr.nvgroup_id,
                    d2=sgr.d2,
                    title=sgr.title,
                    sticker=getSticker(stmpl),
                    persona=persona,
                )

            if sgr.nvEvent == 'CL':  # Видеолекции
                byEvent['CL'].append(edc)
            else:
                byEvent[titleH3].append(edc)

        # *** *** ***

    # *** *** ***

    byEvent = {'CL': []}  # 0 - все кроме видео, CL- видеолекции
    sessArr = []
    persona = None

    if dcUK.cmd == 'showCL':  # call from LK cur-lec-worker(student)
        if dcUK.choosing in ['All', 'C']:  # curator or all
            sessArr = getSessionsGr_GrId(dcUK, group=dcUK.groupC)
            persona = 'Куратор'
            iconList(f'Куратор ({dcUK.titleGr})')

        if dcUK.choosing in ['All', 'L']:  # lector or all
            dcUK.cmd = 'showC2'  # костыль № 734
            sessArr = getSessionsGr_GrId(dcUK, group=dcUK.groupL)
            persona = 'Лектор'
            iconList(f'Лектор ({dcUK.titleGr})')

        if dcUK.choosing in ['All', 'S']:  # worker or all
            sessArr = getSessStByProfId(dcUK)
            persona = 'Сотрудник'
            iconList('Сотрудник')

    elif dcUK.cmd == 'showC3':  # call from LK studen or from office
        sessArr = getSessStByProfId(dcUK)
        persona = 'Сотрудник'
        iconList('Расписание')

    else:  # call from office
        if dcUK.cmd == 'showC2':  # not lector
            persona = 'Куратор'
        sessArr = getSessionsGr_GrId(dcUK, group=dcUK.selected)
        iconList(f"Расписание ({dcUK.titleGr})")  # Все группы|65-60

    byEvent[well('eventsByCode', 'CL')] = byEvent['CL']  # 'Видеолекции'
    del byEvent['CL']  # чтобы видео было последним
    return byEvent


def showC(dcUK):  # эскизы
    byEvent = getSessionKit(dcUK)
    smArr = []
    for titleH3, sessArr in byEvent.items():  # все + видеолекции в конце
        theArr = []
        for ss in sessArr:
            if ss['persona'] == 'Сотрудник':
                btnCmd = 'cmdOpenSess'
                btnPar = f"form={ss['form']}&rsMode=edit&dbAlias=nv_{ss['form']}&unid={ss['pk']}&title={ss['title']}"

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
            title = f'{group}\n{ss["title"]}'  # чтобы было понятно, к какой группе относится событие

            if ss['persona'] == 'Куратор':
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
            sm = _div(titleH3, className='h3', **style(padding=10,), children=[
                    _div(
                        children=theArr,
                        **style(font='700 14px Verdana,Arial', color='#036', textAlign='center'))
            ])

            smArr.append(sm)

    titleH2 = swell('programm')[0]  # задается в справочнике, [0] - название, [1] - описание
    smArr.insert(0, _div(
                        titleH2, className='h2',
                        **style(color='#00f', textDecoration='none')))

    return _div(**style(width='100%', height='100%', overflowY='auto'), children=smArr)

# *** *** ***


btnLogout = _btnD('🔚', 'exitLK', className='propBtn', **style(left=0), title='Logoff')
btnSetting = _btnD(
                '🛠️', 'previewArm', 'newForm=etc&title=Настройки&dbAlias=etc',
                className='propBtn', **style(right=0), title='Масштаб и др. настройки')
btnProfile = _field('openProfile', 'btn', fd=1, className='grenBut')


def showLKphone(table, fioCLS=None):
    if fioCLS:  # for office-mode
        fio, _, pk = fioCLS.partition('|')
        fioCLS = _btnD(fio, 'openProfile2', pk, **style(font='bold 12px Arial', color='#036'))

    return _div(
        className='page51',
        children=[
            btnLogout,
            btnSetting,
            _div(
                **style(maxWidth=WIDTH, margin='auto'),
                children=[
                    _div(className='propfile', children=[
                        btnProfile,
                        fioCLS,
                    ]),
                    _div(
                        **style(overflow='hidden', height='calc(100vh - 32px)'),
                        children=[_tabNew('LK_Table_FD', tabs=table)]
                    )
                ])
        ])

# *** *** ***


def armButtom(su):
    btn = [
        _btnD('Пользователи', 'previewArm', 'newForm=v_profiles&title=Профайлы', className='redBut'),
        _btnD('Программа', 'previewArm', 'newForm=v_content&title=Программа', className='redBut'),
        _btnD('Расписание', 'previewArm', 'newForm=v_schedule&title=Расписание', className='redBut'),
        _btnD('Список групп', 'previewArm', 'newForm=v_groups&title=Список групп', className='redBut'),
        _btnD('Студенты по гр.', 'previewArm', 'newForm=v_students&title=Студенты', className='redBut'),
        _btnD('Платежи', 'previewArm', 'newForm=v_payments&title=Платежи', className='redBut'),
        _btnD('Тр-Фест-Озн.сем', 'previewArm', 'newForm=v_invite&title=Тренинг Фест Озн.сем.', className='redBut'),
        _btnD('Справочники', 'previewArm', 'newForm=v_classifiers&title=Справочники', className='redBut'),
        _btnD('О Т Ч Е Т Ы', 'previewArm', 'newForm=v_reports&title=Отчеты и аналитика&rsMode=edit', className='redBut', **style(margin='10px 20px')),
    ]
    if su:
        btn.append(_btnD('Обр.связь', 'previewArm', 'newForm=v_reports&title=Отчеты и аналитика&rsMode=edit&addUrl:&domain=feedback',
                         className='redBut', **style(margin='10px 20px')))

    return _div(className='armPcBtn', children=btn)


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
                    *labField('Ознакомительный семинар', 'invite', 'lbsd', 'cmd=well&clues=invite', placeholder='Список'),
            ]),
            _div(**style(width=220, display='inline-block', margin=10, textAlign='left', verticalAlign='top'),
                 children=[
                    *labField('Источник информации', 'info', 'lbsd', 'cmd=well&clues=info', placeholder='Список'),
            ]),
            _div(**style(width=150, display='inline-block', margin=10, textAlign='left', verticalAlign='top'),
                 children=[
                    *labField('Роль', 'role', 'lbsd', 'cmd=well&clues=role', placeholder='Список'),
            ]),

            _div(**style(marginTop=15, border='0 solid #036', borderTopWidth=1)),

            # ***

            _div('Проверить личный кабинет пользователя', **style(marginTop=15), className='h3'),
            _div(
                **style(margin=10, width=300, display='inline-block', textAlign='left'),
                children=[
                    *labField('Показать ЛК сотрудника', 'showTutor', 'lbsd', 'cmd=well&clues=tutors2'),
                ]),
            _div(
                **style(margin=10, width=300, display='inline-block', textAlign='left'),
                children=[
                    *labField('Показать ЛК студента', 'showStudent', 'lbsd', 'cmd=well&clues=студент2'),
                ]),
        ])


def showLKpc(table, fioCLS=None, superUser=None):
    '''
    вызывается из офиса для показа доп. вкладок выбранного пользователя
    table - список вкладок
    fioCLS - копка профайл выбранного пользователя
    superUser - boolean для показа доп кнопок (отчеты superUser)
    '''
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
                    btnProfile,  # кнопка "профайл админа"
                    fioCLS,  # кнопка "профайл выбранного пользователя"
                ]),
                _div(**gridStyle('170px 1fr', overflow='hidden', height='calc(100vh - 30px'),
                     children=[
                        armButtom(superUser),  # кнопки СРМ
                        _div(**style(height='inherit', padding=1),
                             children=[_tabNew('LK_Table_FD', tabs=table)]  # вкладки
                             )
                ]),
            ]),

        ])

# *** *** ***


def sstFiler(sst, sgr, dcUK, lastDay):
    '''
    Called from lk_tools.getSessStByProfId
    отсекает лишнее. Фильтры задаются в форме arm_filter.py
    '''

    if dcUK.status == 'A' and sgr.status != 'active':  # кнопка работе
        return

    if dcUK.choosing:  # call from curator-lector-worker
        # не показ эскизы через 1 день после оконч or isEmpty
        if dcUK.filterPlanCL == 'Y' and (sgr.date_end or sgr.date_begin) < lastDay:
            return

        if dcUK.filterEventCL and dcUK.filterEventCL != sgr.nvEvent:
            return

    elif dcUK.cmd == 'showC3':  # call from LK studen
        # не показ эскизы через 1 день после оконч or isEmpty
        if dcUK.filterPlan3 == 'Y' and (sgr.date_end or sgr.date_begin) < lastDay:
            return

        if dcUK.filterEvent3 and dcUK.filterEvent3 != sgr.nvEvent:
            return

        filtField = [('filterAllow3', 'ALLOW_S'), ('filterWas3', 'WAS_S'), ('filterPayment3', 'PAY_S')]
        for k in filtField:  # k[0] - filter(Y or N or ''), k[1] - filedName in sst
            if dcUK[k[0]] == 'Y' and not sst[k[1]]:  # пропустить сст с пустым полем
                return
            if dcUK[k[0]] == 'N' and sst[k[1]]:  # пропустить заполненное
                return

        if dcUK.filterEC3 == 'E' and not sst.esse_s:
            return
        if dcUK.filterEC3 == 'C' and not sst.consultant_s:
            return

        if dcUK.filterFeedBack3 == 'Y':
            if not any([sst[x] for x in sst.keys() if x.startswith('ASSLEC')]):
                return
        elif dcUK.filterFeedBack3 == 'N':
            if any([sst[x] for x in sst.keys() if x.startswith('ASSLEC')]):
                return

        # todo: need delete(from old version)
        if dcUK.status == '0' and not sst.ALLOW_S:
            return
        if dcUK.event and sgr.nvEvent != dcUK.event:
            return

    return True

# *** *** ***


def getSessStByProfId(dcUK):
    # selGrId = dcUK.group.partition('|')[2]  # group=2022-8/Дн|66

    if dcUK.showLK_id and not (dcUK._staff or 'куратор' in dcUK._role):
        return []  # чужие таблицы только куратору и админу

    # groups = set() # todo? У студня м.б. неск групп

    byGroup = []
    studId = dcUK.showLK_id or dcUK._profilePK
    sstArr = list(well('sessionSt_idPr', studId) or []) + well('sessionsGrCommon')
    # !!! well('sessionsGrCommon') - здесь уже сессии общих групп
    lastDay = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # скрыть прошедшие
    for sst in sstArr:
        if sst.sessiongr_id:
            sgr = well('sessionGr_Id', sst.sessiongr_id)
        else:
            sgr = sst  # она и есть сессия группы

        if not sstFiler(sst, sgr, dcUK, lastDay):
            continue

        stmpl = well('sessionTmpl_id', sgr.sessiontmpl_id)

        d = DC(sst)

        d.title = stmpl['title']
        d.sticker = getSticker(stmpl)
        d.form = d.form or 'SessionSt'
        # groups.add(well('groups_groupId', sgr.NVGROUP).title)
        for k in ['d2', 'date_begin', 'date_end', 'nvgroup_id', 'duration', 'nvEvent']:
            d[k] = sgr[k]

        d.persona = dcUK.persona
        byGroup.append(d)

    # dcUK.titleGr = list(groups)
    return sorted(byGroup, key=lambda dc: dc.date_begin)

# *** *** ***


def rightBtnLK(n, na=None):
    '''
    n = '', '2', '3' - curator, lector, student
    na = 'viewbar1' в форме v_shedule
    '''
    return [
        _field(f'changeView{n}', 'band', ['календ|k1', 'событ|e', 'спис|l'],  # , 'к2|k2'
               recalcText=1, className='radioBandNew', title='календарь/эскизы/список', name=na),
        _div(**style(flex=1)),
        _field(f'status{n}', 'band', ['актив|A', 'все|'], className='radioBandNew', recalcText=1, xValue='A'),
    ]

# *** *** ***


scaleEtc = _div(className='scaleEtc', children=[
    _lc('Установите удобный для глаз масштаб'),
    _field(
        'scale_ETC', 'band', ['75%', '90%', '100%', '110%', '125%'],
        **style(maxWidth=300, margin='auto')
    ),
    _btnD('\xa0запомнить\xa0', 'save_etc', className='toolbar-button'),
])

# *** *** ***


def _htmlField(xName, text, **kv):  # , style2=None, className2=None
    xNameU = xName.upper()
    return _div(**kv, children=[
                _field(
                    xName, 'chb', [f'{text} ▼', f'{text} ►'], fileName=xName,
                    className='htmlHelp1', title='сложить/показать', chbView='showHtml'),
                _field(f'HTML_{xNameU}', 'html', name=f'HTML_{xNameU}', className='htmlHelp2')
                ])

# *** *** ***


contacts = _div(**style(height='100%', overflowY='auto', position='relative'), children=[
    # _div(**style(width=400, margin='auto', padding=10, border='1px solid #aaa', background='#fff'),
    _div(
        className='htmlHelp',
        children=[
            _htmlField('requisites.html', 'Реквизиты'),
            ])
    ])

manuals = _div(
            'Инструкции пользователя', className='htmlHelp',
            children=[
                _htmlField('helpStudent.html', 'ЛК студента'),
                _htmlField('helpCurator.html', 'ЛК куратора'),
            ])

# *** *** ***

# def loadHtml(dcUK):
#     html = well(dcUK.xName)
#     if not html:
#         try:
#             with open(os.path.join(BASE_DIR, 'static', 'html', dcUK.xName), encoding='utf-8') as f:
#                 html = f.read()
#                 toWell(html, dcUK.xName)
#         except Exception as ex:
#             html = f'{dcUK.xName}: {ex}'
#             err(html, cat='htmlField')
#     return HttpResponse(html)

# *** *** ***

