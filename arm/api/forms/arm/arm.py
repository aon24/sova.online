# -*- coding: utf-8 -*-
'''
AON 2018

'''
from arm.tools.DC import well, swell, config
from arm.tools.first import err
from arm.api.forms.formTools import _btnEdit, _btnDel, _field, style, _div, _btnD, labelc, \
    gridStyle, _tabNewSber
from arm.api.forms.classPage import Page
from arm.api.forms.lk_tools import showC, showCC, showLKphone, showLKpc, office, \
    rightBtnLK, armButtom
from arm.api.forms.arm.lk_student import office_student, showLKStudent
from arm.api.forms.arm.lk_curator import showLKCurator, getViewCL, getWorkerList, review
from arm.api.forms.tables import paymentsList

import json

# *** *** ***


class arm(Page):
    '''
    HomePage
    Стартовая страница всех ЛК
    В режиме office не кэшируется, т.к. может показывать ЛК любого пользователя
    '''
    _PAGE_ = 1
    _VIEW_ = 1
    form = 'arm'
    title = config.orgName

    def __init__(self, request):
        dcUK = request.dcUK
        self.noCaching = dcUK._staff
        self.dbAlias = 'arm'
        self.jsCssUrl = ['/api/jsv?forms/arm/arm.css', ]
        self.studentOnly = None

        if dcUK._staff:
            self.jsCssUrl += ['/api/jsv?forms/arm/arm.js']
        elif 'куратор' in dcUK._role or 'преподаватель' in dcUK._role:
            self.jsCssUrl += ['/api/jsv?forms/arm/armCL.js']
        elif 'студент' in dcUK._role:
            self.studentOnly = True
            self.jsCssUrl += ['/api/jsv?forms/arm/armStMb.js']
        super().__init__(request)

# *** *** ***

    def page(self, request):
        if not self._staff:
            return showLKStudent(self) if self.studentOnly else showLKCurator(self)

        # ***
        curator = lector = student = None
        dcUK = request.dcUK
        fioCLS = None

        profile = dcUK.showLK
        dc = profile and well('profiles', profile)
        if dc:
            curator = 'куратор' in dc.role and self.curatorSheet()

            lector = 'преподаватель' in dc.role and self.lectorSheet()

            dcUK._studentProfilePK = dc.id  # чтобы показать офису плтежи студента

            fio = dc.full_name.partition(' ')[0]
            if 'студент' in dc.role:
                fioCLS = f' <Студ: {fio}>|{dc.id}'
                student = ('студент', office_student(self), 80)
            else:
                fioCLS = f' <Сотр: {fio}>|{dc.id}'
                student = ('сотрудник', office_student(self), 100)

        if self._userAgent == 'mobile':
            tabs = [
                ('🦉', armButtom(dcUK._superUser), 50),
                ('офис', office(), 65),
                ('куратор', curator, 80),
                ('препод', lector, 80),
                student,
            ]
            return showLKphone(tabs, fioCLS=fioCLS)
        else:
            tabs = [
                ('офис', office(), 65),
                ('куратор', curator, 80),
                ('препод', lector, 80),
                student,
            ]
            return showLKpc(tabs, fioCLS=fioCLS, superUser=dcUK._superUser)

    # *** *** ***

    def curatorSheet(self):
        # Curator
        divUL1 = _div(children=[
            labelc('Расписание', **style(margin='10px 0')),
            _field(
                'leftList', 'band', [], className='newBand',
                recalcText=1, rowLength=1,
                **style(width=120, textAlign='center')),  # список групп
        ])

        divUL2 = _div(children=[
            labelc('Список сессий', **style(margin='10px 0')),
            _field('upList', 'band', [], className='newBandRed',
                   noRecalc=1, recalcText=1, rowLength=1, noAlias=1,
                   **style(width=120, textAlign='center')),  # it is buttons
        ])

        if self._userAgent == 'mobile':
            self.leftWidth = 0
            self.leftList = None

            self.upField = _div(**gridStyle('140px 2px 140px', margin='auto', background='#fff'), children=[
                divUL1,
                _div(**style(background='#555')),
                divUL2,
            ])
        else:
            self.leftWidth = 130
            self.upField = None

            self.leftList = _div(children=[
                divUL1,
                _div('* * *', **style(margin='10px 0', textAlign='center')),
                divUL2,
            ])

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 0px 0', background='transparent'),
            rightBtn=rightBtnLK(''),
        )

        url = 'form=arm&cmd=getSelected&selected={leftList}&status={status}&view={changeView}&plan={plan}'
        previewUrl = 'dbAlias=nv_SessionGr'
        self.mainList = _div(**style(height='100%'), children=[
            _field('mainList', 'view', name='mainList', limit=100000, url=url, previewUrl=previewUrl, noMount=1),
            _field('showCourse', 'json', **style(height='100%', background='#88440020'), name='showCL')
        ])

        return _tabNewSber('lk2_Table_FD', [  # сверху 2 иконки Расписание-LK
                                ('/image/bands/scheduling.png', self.sham(), 'Расписание'),
                                ('/image/bands/lk.png', review, 'ЛК'),
                                # ('/image/bands/owl.png', contacts, 'Контакты'),
                            ], 60)

    # self.sham()

    # *** *** ***

    def getData(self, dcUK):
        # curator
        # для msgListBox выбрать сессию
        #
        if dcUK.cmd == 'getSessTemplList':
            data = swell('sessionTmpl_nve_band', dcUK.nve)  # для msgListBox выбрать сессию для группы

        #
        # stdent
        # make Cube
        elif dcUK.cmd == 'getEdges':
            data = {}
            dcUK.cmd = 'showC3'
            dcUK.dateZ_id = 'dateZ_3'
            view = dcUK.view  # view=k1k2(shiftMonth) or k1k2e(all edges)
            if 'l' == view:
                mainDocs = getWorkerList(dcUK)
                mainDocs = [[x[0], x[1]] for x in sorted(mainDocs, key=lambda x: x[2])]
                data = {'mainDocs': mainDocs, 'refsDocs': None}
            else:
                if 'k1' in view:
                    dcUK.view = 'k1'
                    data['calendar1m'] = showCC(dcUK)
                if 'e' in view:
                    data['images'] = showC(dcUK)
                if 'k2' in view:
                    dcUK.view = 'k2'
                    data['calendar2m'] = showCC(dcUK)

        # curator - lector - worker
        #
        elif dcUK.cmd == 'showCL':
            if dcUK.view == 'l':
                data = getViewCL(dcUK)
            else:
                dcUK.dateZ_id = 'dateZ_CL'
                if dcUK.view == 'k1':  # 'к1', 'к2', 'эскиз', 'спис'
                    data = showCC(dcUK)
                elif dcUK.view == 'k2':
                    data = showCC(dcUK)
                else:
                    data = showC(dcUK)

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
            if dcUK.view == 'k1':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == 'k2':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # lector
        elif dcUK.cmd == 'showC2':
            dcUK.dateZ_id = 'dateZ_2'
            if dcUK.view == 'k1':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == 'k2':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # stdent
        #
        elif dcUK.cmd == 'showC3':
            dcUK.dateZ_id = 'dateZ_3'
            if dcUK.view == 'k1':  # 'к1', 'к2', 'эскиз', 'спис'
                data = showCC(dcUK)
            elif dcUK.view == 'k2':
                data = showCC(dcUK)
            else:
                data = showC(dcUK)

        # stdent
        #
        elif dcUK.cmd == 'getSelected3':
            data = {'mainDocs': getWorkerList(dcUK), 'refsDocs': None}

        elif dcUK.cmd == 'getTable':
            if dcUK.showLK_id and not (dcUK._staff or 'куратор' in dcUK._role):
                data = [_div('Access denied')]  # чужие таблицы только куратору и админу
            elif dcUK.table == 'payments':
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
        ls = dcUK.selected

        sgrLs = []
        for grId in ls.split('-'):
            sgrLs += well('sessionsGr_GrId', grId)

        sgrLs.sort(key=lambda dc: dc.title)

        # plan закомментирован (всегда "")
        # days = 1 if dcUK.plan == '0' else 100000
        # yesterday = datetime.now() - timedelta(days=days)
        # last = yesterday.strftime("%Y-%m-%d")

        for sgr in sgrLs:
            # plan закомментирован (всегда "")
            # dateEnd = sgr.date_end or sgr.date_begin
            # if dateEnd < last:  # не показ эскизы через 1 день после оконч or isEmpty
            #     continue

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

            pk = sgr.id

            sst = well('sessionTmpl_id', sgr.sessionTmpl_id)
            title = _div(
                f"{sst.title}\nс {d1} по {d2}",
                className='mCell', s2=1, br=1, **style(width='100%', letterSpacing=1, textAlign='left')
            )

            if dcUK.cmd == 'getSelected':  # curator
                row = _div(
                    **style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto'),
                    children=[title, _btnEdit('cmdEdit', pk), _btnDel('cmdDel', f'mainList|{pk}|nv_SessionGr')]
                )
            else:  # lector
                row = _div(
                    **style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto'),
                    children=[title, _btnEdit('cmdEdit12', pk)]
                )

            mainDocs.append([pk, row])

        return {'mainDocs': mainDocs, 'refsDocs': None}

    # *** *** ***

    def lectorSheet(self):
        # lector
        self.leftWidth = 105
        self.upField = _btnD(
            'Программа',
            'previewArm', 'newForm=v_content&title=Программа',
            className='btnArm', **style(padding=10, fontSize=18, margin='5px auto', display='block', width=200)
        )

        self.leftList = _field('leftList2', 'band', [])  # groups)

        self.viewbar = self.makeViewbar(
            **style(gridTemplateColumns='1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK('2'),
        )

        url = 'form=arm&cmd=getSelected2&showTutor={showTutor}&selected={leftList2}&status={status2}&view={changeView2}&plan={plan2}'
        previewUrl = 'dbAlias=nv_SessionGr'

        self.mainList = _div(**style(height='100%'), children=[
            _field('mainList2', 'view', name='mainList2', limit=100000, url=url, previewUrl=previewUrl, noMount=1),
            _field('showCourse2', 'json', **style(height='100%'), name='showCL2')
        ])

        sh = self.sham()
        # sh['attributes']['style']['backgroundColor'] = '#f4fffa'
        return sh

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

            # группы сотрудника
            dcUK.doc.workerGroups = json.dumps(getStudentGroups(pk), ensure_ascii=False)

            # слишком сложно: в гл. ленте _tabNewSber, в иконках 3 дива
            if prof.FILES1_:
                try:
                    js = json.loads(prof.FILES1_)
                    icon = _div(
                        **style(height=70, width=60), children=[
                            _div(
                                **style(
                                    height=60, backgroundSize='100% 100%',
                                    backgroundImage=f'url("/api/xImage?path={js[0]["path"]}&type={js[0]["type"]}")')),
                            _div('ЛК'),
                            ])
                    dcUK.doc.lkIcon = json.dumps(icon, ensure_ascii=False)
                except Exception as ex:
                    err(f'json.loads for "{prof.FULL_NAME}": {ex}', cat='profile-photo')

        dcUK.doc.fullName = dcUK.fullName
        l, _, r = dcUK.fullName.partition(' ')
        fn = f'{l} {r[0]}.' if r else l
        dcUK.doc.openProfile = f"{fn}|openProfile{'' if dcUK._profilePK else '|1'}"
        dcUK.doc.studentOnly = self.studentOnly

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

# *** *** ***


def getStudentGroups(studId):
    groups = set()  # У студня м.б. неск групп
    sstArr = list(well('sessionSt_idPr', studId) or []) + well('sessionsGrCommon')
    # !!! well('sessionsGrCommon') - здесь уже сессии общих групп
    for sst in sstArr:
        if sst.sessiongr_id:
            sgr = well('sessionGr_Id', sst.sessiongr_id)
        else:
            sgr = sst  # она и есть сессия группы
        groups.add(well('groups_groupId', sgr.NVGROUP).title)

    return list(groups)
