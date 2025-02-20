# -*- coding: utf-8 -*-
'''
AON 2018

'''
from arm.tools.DC import well, config
from arm.tools.first import err
from arm.api.forms.formTools import _btnEdit, _btnDel, _field, style, _div, _btnD
from arm.api.forms.classPage import Page
from arm.api.forms.lk_tools import showC, showCC, showLK, showLKpc, office, rightBtnLK
from arm.api.forms.arm.lk_student import getViewStudent, lk_student
from arm.api.forms.tables import paymentsList

import json
from datetime import datetime, timedelta

# *** *** ***

logoff = _div(className='page51', **style(textAlign='center', paddingTop=150), children=[
    _btnD('Profile not found', 'logout', title='logout', **style(display='inline', padding=5, fontSize=30)),
])


class arm(Page):
    def __init__(self, form):
        self.form = 'arm'
        self.title = config.orgName
        self.noCaching = True
        self.dbAlias = 'arm'
        self.jsCssUrl = [ f'/api/jsv?forms/arm/events.css']
        super().__init__(form)

# *** *** ***

    def page(self, request):
        dcUK = request.dcUK
        studentOr = 'студент'

        fullName = dcUK.fullName
        if dcUK._staff:
            fioCLS = dc = None
            curator = lector = student = None

            profile = dcUK.showLK
            dc = profile and well('profiles', profile)
            if dc:
                curator = 'куратор' in dc.role and self.coratorSheet(getCuratorGroups(dc))

                lector_groups = getLectorGroups(dc.full_name)
                lector = ('преподаватель' in dc.role or lector_groups) and self.lectorSheet(sorted(list(lector_groups), reverse=True))

                sstArr = well('sessionSt_idPr', profile) or well('sessionsGrCommon')
                dcUK._studentProfilePK = dc.pk  # чтобы показать офису плтежи студента
                student = sstArr and lk_student(self, dcUK)

                fio = dc.full_name.partition(' ')[0]
                if dc.role == 'студент':
                    fioCLS = f' <Студ: {fio}>|{dc.pk}'
                else:
                    fioCLS = f' <Сотр: {fio}>|{dc.pk}'
                    studentOr = 'сотрудник'

            if dcUK._USERAGENT == 'mobile':
                tabs = [
                    ('🦉', self.armPageAdmin(), 50),
                    ('офис', office()),
                    ('куратор', curator),
                    ('препод', lector),
                    (studentOr, student),
                ]
                return showLK(tabs, fullName, 100, noProf=not dcUK._profilePK, fioCLS=fioCLS)
            else:
                tabs = [
                    ('офис', office()),
                    ('куратор', curator),
                    ('препод', lector),
                    (studentOr, student),
                ]
                return showLKpc(tabs, fullName, 100, noProf=not dcUK._profilePK, fioCLS=fioCLS)

        # *** *** ***

        elif not dcUK._profilePK:
            return logoff

        # *** *** ***

        lector_groups = curator = sstArr = None
        role = dcUK._role
        if 'студент' in role:
            if any(x in role for x in ['куратор', 'преподаватель']):
                studentOr = 'сотрудник'
                sstArr = well('sessionSt_idPr', dcUK._profilePK)
            else:
                return lk_student(self, dcUK)  # для студня отдельная форма

        if 'куратор' in role:
            dcc = well('profiles', dcUK._profilePK)
            curator = dcc and self.coratorSheet(getCuratorGroups(dcc))

        if 'преподаватель' in role:
            lector_groups = getLectorGroups(fullName)

        lector = 'преподаватель' in role and self.lectorSheet(sorted(list(lector_groups), reverse=True))
        student = sstArr and lk_student(self, dcUK)

        tabs = [
            ('куратор', curator),
            ('препод', lector),
            (studentOr, student),
        ]

        return showLK(tabs, fullName, 100, noProf=not dcUK._profilePK)

        # *** *** *** '☰'

    def coratorSheet(self, curator_groups):
        # Curator
        self.leftWidth = 105
        self.upField = None
        if len(curator_groups) > 1:
            ls = [s.partition('|')[2] for s in curator_groups]
            groups = [f"Все группы|{'-'.join(ls)}"] + curator_groups
        else:
            groups = curator_groups

        self.leftList = _div(children=[
            _field('leftList', 'band', groups, className='list1str', recalcText=1, rowLength=1),
            _div('* * *', **style(margin='10px 0', textAlign='center')),
            _field('upList', 'band', curator_groups, noRecalc=1, recalcText=1, rowLength=1),  # it is buttons
        ])

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK(''),
        )

        url = '/api/getData?form=arm&cmd=getSelected&selected={leftList}&status={status}&view={changeView}&plan={plan}'
        previewUrl = 'dbAlias=nv_SessionGr'
        self.mainList = _div(**style(height='100%'), children=[
            _field('mainList', 'view', name='mainList', limit=100000, url=url, previewUrl=previewUrl, noMount=1),
            _field('showCourse', 'json', **style(height='100%'), name='showCL')
        ])
        return self.sham()

    # *** *** ***

    def getData(self, dcUK):
        # curator
        #
        # для msgListBox выбрать сессию
        #
        if dcUK.cmd == 'getSessTemplList':
            data = well('sessionTmpl_nve_band', dcUK.nve)  # для msgListBox выбрать сессию для группы

        # curator - lector
        #
        elif dcUK.cmd in ['getSelected', 'getSelected2']:
            try:
                data = self.getView(dcUK)
            except Exception as ex:
                err(f'{ex}', cat='arm.getData.getView')
                data = {'mainDocs': [('123', f'ERROR: {ex}'), ], 'refsDocs': []}

        # curator
        #
        elif dcUK.cmd == 'showC':
            dcUK.dateZ_id = 'dateZ_'
            if dcUK.view == '0':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == '1':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # lector
        elif dcUK.cmd == 'showC2':
            dcUK.dateZ_id = 'dateZ_2'
            if dcUK.view == '0':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == '1':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # stdent
        #
        elif dcUK.cmd == 'showC3':
            dcUK.dateZ_id = 'dateZ_3'
            if dcUK.view == '0':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == '1':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # stdent
        #
        elif dcUK.cmd == 'getSelected3':
            data = getViewStudent(dcUK)
        elif dcUK.cmd == 'getTable':
            if dcUK.table == '0':
                data = paymentsList(dcUK)
            elif dcUK.table == '1':
                data = [_div('')]
            else:
                data = [_div('')]

        elif dcUK.cmd == 'changeStatus':
            dc = well('profiles', dcUK.showLK_id or dcUK._profilePK)
            if dcUK.lk == '':  # curator
                groups = getCuratorGroups(dc, dcUK.status)
                if len(groups) > 1:
                    ls = [s.partition('|')[2] for s in groups]
                    data = [[f"Все группы|{'-'.join(ls)}"] + groups, groups]
                else:
                    data = [groups, groups]
            elif dcUK.lk == '2':  # lector
                data = getLectorGroups(dc.full_name, dcUK.status)
            else:
                data = []
        else:
            err(f'invalid cmd: {dcUK.cmd}', cat='arm.getData')
            data = {'mainDocs': [('123', f'invalid cmd: {dcUK.cmd}'), ], 'refsDocs': []}
        return json.dumps(data, ensure_ascii=False)

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []
        titleGr, _, ls = dcUK.selected.partition('|')

        sgrLs = []
        for grId in ls.split('-'):
            sgrLs += well('sessionsGr_GrId', grId)

        sgrLs.sort(key=lambda dc: dc.date_begin + dc.title)

        days = 1 if dcUK.plan == '0' else 100000
        yesterday = datetime.now() - timedelta(days=days)
        last = yesterday.strftime("%Y-%m-%d")

        for sgr in sgrLs:
            dateEnd = sgr.date_end or sgr.date_begin
            if dateEnd < last:  # не показ эскизы через 1 день после оконч or isEmpty
                continue

            if dcUK.status == '0' and sgr.status != 'active':  # кнопка работе
                continue

            if dcUK.cmd == 'getSelected2':
                fio = dcUK.showTutor
                if fio:
                    if fio not in sgr.lector:
                        continue

                elif dcUK.fullName not in sgr.lector:
                    continue

            d1 = sgr.D('date_begin') or '--.--.--'
            d2 = sgr.D('date_end') or '--.--.--'

            pk = sgr.pk

            sst = well('sessionTmpl_id', sgr.sessionTmpl_id)
            title = _div(f"{sst.title}\nс {d1} по {d2}",
                className='mCell', s2=1, br=1, **style(width='100%', letterSpacing=1, textAlign='left'))

            if dcUK.cmd == 'getSelected':  # curator
                row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                    children=[title, _btnEdit('cmdEdit', pk), _btnDel('cmdDel', f'mainList|{pk}|nv_SessionGr')])
            else:  # lector
                row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto'),
                    children=[title, _btnEdit('cmdEdit12', pk)])

            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs,'refsDocs': None}

    # *** *** ***

    def lectorSheet(self, groups):
        # lector
        self.leftWidth = 105
        self.upField = _btnD('Программа',
                'previewArm', 'newForm=v_content&title=Программа&unid=1&dbAlias=nv_SessionTmpl',
                className='btnArm', **style(padding=10, fontSize=18, margin='5px auto', display='block', width=200))

        ls = [s.partition('|')[2] for s in well('commonGroups') + groups]
        self.leftList = _field('leftList2', 'band', groups)

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK('2'),
        )

        url = '/api/getData?form=arm&cmd=getSelected2&showTutor={showTutor}&selected={leftList2}&status={status2}&view={changeView2}&plan={plan2}'
        previewUrl = 'dbAlias=nv_SessionGr'

        self.mainList = _div(**style(height='100%'), children=[
            _field('mainList2', 'view', name='mainList2', limit=100000, url=url, previewUrl=previewUrl, noMount=1),
            _field('showCourse2', 'json', **style(height='100%'), name='showCL2')
        ])

        sh = self.sham()
        # sh['attributes']['style']['backgroundColor'] = '#f4fffa'
        return sh

    # *** *** ***

    def armPageAdmin(self):
        buttonSubj = _btnD('Содержание',
                'previewArm', 'newForm=v_content&title=Содержание',
                className='btnArm', **style(width='100%', marginTop=10, padding='10px 5px'))

        buttonPay = _btnD('Платежи',
                'previewArm', 'newForm=v_payments&title=Платежи',
                className='btnArm', **style(width='100%', marginTop=10, padding='10px 5px'))

        buttonGr = _btnD('Список групп',
                'previewArm', 'newForm=v_groups&title=Список групп',
                className='btnArm', **style(width='100%', marginTop=10, padding='10px 5px'))
        buttonShed = _btnD('Расписание',
                'previewArm', 'newForm=v_schedule&title=Расписание',
                className='btnArm', **style(width='100%', marginTop=10, padding='10px 5px'))
        buttonStByGr = _btnD('Студенты по группам',
                'previewArm', 'newForm=v_students&title=Студенты',
                className='btnArm', **style(width='100%', marginTop=10, padding='10px 5px'))
        buttonProf = _btnD('Пользователи',
                'previewArm', 'newForm=v_profiles&title=Профайлы',
                className='btnArm', **style(display='block', width=250, margin='10px auto', padding='10px 5px'))

        buttonMore = _btnD('Тренинг Фест Озн.сем',
                'previewArm', 'newForm=v_more&title=Тренинг Фест Озн.сем.',
                className='btnArm', **style(display='block', width=250, margin='10px auto', padding='10px 5px'))
        buttonCls = _btnD('Справочники',
                'previewArm', 'newForm=v_classifiers&title=Справочники',
                className='btnArm', **style(display='block', width=250, margin='10px auto', padding='10px 5px'))

        return _div(
            **style(margin='auto', textAlign='center', height='100%', overflow='auto'),
            children=[
                buttonProf,

                _div(
                **style(width=250, display='inline-block', margin=15, textAlign='center', verticalAlign='top'),
                children=[
                    buttonShed,
                    buttonSubj,
                    buttonStByGr,
                ]),

                _div(
                **style(width=250, display='inline-block', margin=15, textAlign='center', verticalAlign='top'),
                children=[
                    buttonGr,
                    buttonPay,
                    buttonMore,
                ]),
                buttonCls,

        ])

    # *** *** ***

    def queryOpen(self, dcUK):
        dcUK.doc.fullName = dcUK.fullName
        dcUK.doc._page_ = 1

# *** *** ***


def getCuratorGroups(dc, status='0'):
    if dc and 'куратор' in dc.role and dc.curator_groups:
        curator_groups = []
        for g in dc.curator_groups.split('\n'):
            grT, _, grId = g.partition('|')
            grDC = well('groups_groupId', grId)
            if grDC:
                if status == '0':
                    if grDC.status == 'active':
                        curator_groups.append(g)
                else:  # all
                    if grDC.status == 'active':
                        curator_groups.append(g)
                    else:
                        curator_groups.append(f'{grT}(A)|{grId}')
        if curator_groups:
            return well('commonGroups') + sorted(curator_groups, reverse=True)

    return []
# *** *** ***


def getLectorGroups(full_name, status='0'):
    lector_groups = set()
    sgrArr = [d for d in well('sessionsGr_All') if full_name in d.lector]
    for sgr in sgrArr:
        grDC = well("groups_groupId", sgr.nvgroup_id)
        if grDC:
            if status == '0':
                if grDC.status == 'active':
                    lector_groups.add(f'{grDC.title}|{grDC.id}')
            else:
                if grDC.status == 'active':
                    lector_groups.add(f'{grDC.title}|{grDC.id}')
                else:
                    lector_groups.add(f'{grDC.title}(A)|{grDC.id}')
    groups = sorted(list(lector_groups), reverse=True)
    if len(groups) > 1:
        ls = [s.partition('|')[2] for s in groups]
        groups.insert(0, f"Все группы|{'-'.join(ls)}")
    return groups

