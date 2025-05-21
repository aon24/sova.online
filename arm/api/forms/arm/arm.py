# -*- coding: utf-8 -*-
'''
AON 2018

'''
from arm.tools.DC import well, swell, config
from arm.tools.first import err
from arm.api.forms.formTools import _btnEdit, _btnDel, _field, style, _div, _btnD
from arm.api.forms.classPage import Page
from arm.api.forms.lk_tools import showC, showCC, showLK, showLKpc, office, rightBtnLK
from arm.api.forms.arm.lk_student import getViewStudent, lk_student, showLKStudent
from arm.api.forms.tables import paymentsList

import json
from datetime import datetime, timedelta

# *** *** ***

logoff = _div(className='page51', **style(textAlign='center', paddingTop=150), children=[
    _btnD('Profile not found', 'logout', title='logout', **style(display='inline', padding=5, fontSize=30)),
])


class arm(Page):

    def __init__(self, request):
        self.form = 'arm'
        self.title = config.orgName
        self.noCaching = request.dcUK._staff
        self.dbAlias = 'arm'
        self.styles = '<link href="/static/fonts/home.css" rel="stylesheet">\n'
        # self.styles = '<link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">\n'
        super().__init__(request)

# *** *** ***

    def page(self, request):
        curator = lector = student = None
        if self._staff:
            dcUK = request.dcUK
            fioCLS = None

            profile = dcUK.showLK
            dc = profile and well('profiles', profile)
            if dc:
                curator = 'куратор' in dc.role and self.coratorSheet()

                lector = 'преподаватель' in dc.role and self.lectorSheet()

                dcUK._studentProfilePK = dc.pk  # чтобы показать офису плтежи студента

                fio = dc.full_name.partition(' ')[0]
                if dc.role == 'студент':
                    fioCLS = f' <Студ: {fio}>|{dc.pk}'
                    student = ('студент', lk_student(self), 80)
                else:
                    fioCLS = f' <Сотр: {fio}>|{dc.pk}'
                    student = ('сотрудник', lk_student(self), 100)

            if self._userAgent == 'mobile':
                tabs = [
                    ('🦉', self.armPageAdmin(), 50),
                    ('офис', office(), 65),
                    ('куратор', curator, 80),
                    ('препод', lector, 80),
                    student,
                ]
                return showLK(tabs, fioCLS=fioCLS)
            else:
                tabs = [
                    ('офис', office(), 65),
                    ('куратор', curator, 80),
                    ('препод', lector, 80),
                    student,
                ]
                return showLKpc(tabs, fioCLS=fioCLS)

        # *** *** ***

        if self._role == 'студент':
            return showLKStudent(self)  # для студня отдельная форма

        student = lk_student(self)

        if 'куратор' in self._role:
            curator = self.coratorSheet()

        if 'преподаватель' in self._role:
            lector = self.lectorSheet()

        tabs = [
            ('куратор', curator, 80),
            ('препод', lector, 80),
            ('сотрудник', student, 100),
        ]

        return showLK(tabs)

        # *** *** *** '☰'

    def coratorSheet(self):
        # Curator
        self.leftWidth = 105
        self.upField = None

        self.leftList = _div(children=[
            _field('leftList', 'band', [], className='list1str', recalcText=1, rowLength=1),  # список групп
            _div('* * *', **style(margin='10px 0', textAlign='center')),
            _field('upList', 'band', [], noRecalc=1, recalcText=1, rowLength=1),  # it is buttons
        ])

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK('', self._userAgent),
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
            data = swell('sessionTmpl_nve_band', dcUK.nve)  # для msgListBox выбрать сессию для группы

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
                data = getCuratorGroups(dc, dcUK.status)
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
        ls = dcUK.selected.partition('|')[2]

        sgrLs = []
        for grId in ls.split('-'):
            sgrLs += well('sessionsGr_GrId', grId)

        sgrLs.sort(key=lambda dc: dc.title)

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

    def lectorSheet(self):
        # lector
        self.leftWidth = 105
        self.upField = _btnD('Программа',
                'previewArm', 'newForm=v_content&title=Программа',
                className='btnArm', **style(padding=10, fontSize=18, margin='5px auto', display='block', width=200))

        self.leftList = _field('leftList2', 'band', [])  # groups)

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK('2', self._userAgent),
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
        st = dict(width=250, marginTop=10, padding='10px 5px')

        buttonProf = _btnD('Пользователи', 'previewArm', 'newForm=v_profiles&title=Пользователи', className='btnArm', style=st)

        buttonProgramm = _btnD('Программа', 'previewArm', 'newForm=v_content&title=Программа', className='btnArm', style=st)
        buttonGr = _btnD('Список групп', 'previewArm', 'newForm=v_groups&title=Список групп', className='btnArm', style=st)
        buttonShed = _btnD('Расписание', 'previewArm', 'newForm=v_schedule&title=Расписание', className='btnArm', style=st)

        buttonStByGr = _btnD('Студенты по группам', 'previewArm', 'newForm=v_students&title=Студенты', className='btnArm', style=st)
        buttonPay = _btnD('Платежи', 'previewArm', 'newForm=v_payments&title=Платежи', className='btnArm', style=st)
        buttonMore = _btnD('Тренинг Фест Озн.сем', 'previewArm', 'newForm=v_invite&title=Тренинг Фест Озн.сем.', className='btnArm', style=st)

        buttonReport = _btnD('О Т Ч Е Т Ы', 'previewArm', 'newForm=v_reports&title=Отчеты и аналитика&rsMode=edit', className='btnArm', style=st)

        return _div(
            **style(margin='auto', textAlign='center', height='100%', overflow='auto'),
            children=[
                _div(children=[buttonProf]),

                _div(
                **style(width=250, display='inline-block', margin=15, textAlign='center', verticalAlign='top'),
                children=[
                    buttonProgramm,
                    buttonShed,
                    buttonGr,
                ]),

                _div(
                **style(width=250, display='inline-block', margin=15, textAlign='center', verticalAlign='top'),
                children=[
                    buttonStByGr,
                    buttonPay,
                    buttonMore,
                ]),
                _div(children=[buttonReport]),

        ])

    # *** *** ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        if dcUK._staff:
            pk = dcUK.showLK or dcUK._profilePK
        else:
            pk = dcUK._profilePK
        prof = well('profiles', pk)
        if prof:
            if 'куратор' in prof.role:
                dcUK.doc.curatorGroups = json.dumps(getCuratorGroups(prof), ensure_ascii=False)
            if 'преподаватель' in prof.role:
                dcUK.doc.lectorGroups = json.dumps(getLectorGroups(prof.full_Name), ensure_ascii=False)

        dcUK.doc.fullName = dcUK.fullName
        dcUK.doc.openProfile = f"{dcUK.fullName}|openProfile{'' if dcUK._profilePK else '|1'}"

        dcUK.doc._page_ = 1

# *** *** ***


def getCuratorGroups(dc, status='0'):
    if dc and 'куратор' in dc.role and dc.curator_groups:
        groups = []
        for g in dc.curator_groups.split('\n'):
            grT, _, grId = g.partition('|')
            grDC = well('groups_groupId', grId)
            if grDC:
                if status == '0':
                    if grDC.status == 'active':
                        groups.append(g)
                else:  # all
                    if grDC.status == 'active':
                        groups.append(g)
                    else:
                        groups.append(f'{grT}(A)|{grId}')
        if groups:
            groups.sort(reverse=True)
            if len(groups) > 1:
                ls = [s.partition('|')[2] for s in groups]
                return [[f"Все группы|{'-'.join(ls)}"] + groups, groups]
            else:
                return [groups, groups]

    return [[], []]

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

