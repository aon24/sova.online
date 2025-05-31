from arm.tools.first import snd, err
from arm.tools.DC import toWell, well, swell, toSwell, clearSwell, clearWell, DC, getBody, config
from arm.tools.common import setVersionJS, cleanPhone
from arm.settings import BASE_DIR, STATIC_DIR

from time import time
import traceback
import os

groupsNoByTitle = {}
groupsTitleByNo = {}


def loadWell(key, param=None):
    if well('busy'):
        if key != 'SessionSt':
            toWell(1, 'reloadWell')
            err(f'Busy for key={key}', cat='loadWell')
        return

    try:
        if key == 'all':
            tm = time()
            clearWell('forms')

            try:
                dirr = os.path.join(BASE_DIR, 'arm', 'api', 'react')
                fn = os.path.join(dirr, 'index.html')
                with open(fn, 'r', encoding='utf-8') as f:
                    buf = setVersionJS(f.read(), BASE_DIR)[0]
                    toWell(buf, 'index.html')
                fn = os.path.join(STATIC_DIR, 'home', 'manifest.json')
                with open(fn) as f:
                    buf = f.read().replace('{% site %}', config.host)
                    toWell(buf, 'manifest.json')
            except:
                err(f'file "{fn}" not loaded', cat='loadWell')

            if not loadCls():
                err('Cls (and all...) not loaded', cat='loadWell')
                return

            loadGroups()
            loadSessionTmpl()
            loadSessionGr()
            loadProfiles()
            createSessionSt()
            loadPayments()
            loadModule()
            loadReport()
            loadLanding()

            toSwell(['2d', '3d', '3d+'], '3dKeys')

            snd(f'Runtime: {int((time()-tm)*1000)} ms', cat='loadWell')
            return

        if key == 'Classifier':
            loadCls()
        elif key == 'Profile':
            loadProfiles()
            if param != 'noSgr':
                createSessionSt()
        elif key == 'NVGroup':
            loadGroups()
        elif key == 'SessionTmpl':
            loadSessionTmpl()
            loadSessionGr()
        elif key in ['SessionGr']:
            loadSessionGr()
            createSessionSt()
        elif key == 'SessionSt':
            createSessionSt()
        elif key == 'Payment':
            loadPayments()
        elif key == 'Module':
            loadModule()
        elif key == 'Report':
            loadReport()
        elif key == 'Landing':
            loadLanding()

        # snd(f'Runtime: {int((time()-tm)*1000)} ms. key={key}, param={param}', cat='loadWell')

    except Exception as ex:
        toWell(0, 'busy')
        err(f'key={key}\n{ex}\n{traceback.format_exc()}', cat='loadWell')

# *** *** ***


def loadCls():
    from nv.models import Classifier

    classifiers = []
    for cls in Classifier.docs.values().all():
        dc = getBody(cls)
        classifiers.append(dc)
        titles = dc.title.split('\n')

        for title in titles:
            if dc.list:
                arr = dc.list.split('\n')
                if title == 'events':
                    evs, esh = [], []
                    for it in arr:
                        tx, code, short, sticker = f'{it}|||'.split('|')[:4]
                        evs.append(f'{tx}|{code}')
                        esh.append(f'{short}|{code}')
                        toWell(tx, 'eventsByCode', code)
                        toWell(sticker, 'stickerByCode', code)

                    toSwell(evs, 'events')
                    esh.insert(0, 'Все|')
                    toSwell(esh, 'shortEvents')
                else:
                    toSwell(arr, title)
            elif dc.formula:
                try:
                    toSwell(eval(dc.formula), title)
                except Exception as ex:
                    err(f'{title} => {ex}', cat='loadCls')

    toSwell(classifiers, 'classifiers')  # for view "Справочники"
    return True


def loadModule():
    from nv_lm.models import Module

    modules = []
    turnOnList = []
    for m in Module.docs.all().order_by('-id').values():
        dc = getBody(m)
        modules.append(dc)
        if dc.turn_on:
            turnOnList.append(dc)

    toWell(modules, 'modules')
    toWell(turnOnList, 'turnOnList')


def loadReport():
    from nv_reports.models import Report

    reports = []
    turnOnReport = []
    for m in Report.docs.all().order_by('-id').values():
        dc = getBody(m)
        if dc.form in ['html', 'Report']:
            reports.append(dc)
        if dc.turn_on and dc.scheduled:
            turnOnReport.append(dc)

    toWell(reports, 'reports')
    toWell(turnOnReport, 'turnOnReport')


def loadSessionGr():
    from nv.models import SessionGr

    sessionsGr_GrId = {}
    sessionsGr_GrId_band = {}
    sessionsGr_All = []  # for shedule
    sessionsGrCommon = []

    clearWell('sessionGr_Id')  # for stickers

    for session in SessionGr.docs.values().all():
        dc = getBody(session)
        stmpl = well('sessionTmpl_id', dc.sessiontmpl_id)
        if not stmpl:  # шаблон был удален
            continue

        if dc.commonGroups:
            dc.form = 'SessionGr'
            sessionsGrCommon.append(dc)

        nvgroup = dc.nvgroup_id  # title
        sessionsGr_GrId[nvgroup] = sessionsGr_GrId.get(nvgroup, [])
        sessionsGr_GrId_band[nvgroup] = sessionsGr_GrId_band.get(nvgroup, [])

        if session['date_begin']:  # у группы есть сессия с датой
            dc.d2 = session['date_begin'].strftime('%d.%m.%y')
            date_end = dc.D('date_end')
            if date_end:
                dc.d2 += f'-{date_end[:6]}{date_end[-2:]}'

        dc.nvEvent = stmpl.nvEvent
        dc.title = stmpl.title

        sessionsGr_GrId[nvgroup].append(dc)
        sessionsGr_GrId_band[nvgroup].append(f'{dc.date_begin}|{dc.title}|{dc.pk}|{dc.status}')
        sessionsGr_All.append(dc)

        toWell(dc, 'sessionGr_Id', dc.pk)

    clearSwell('sessionsGr_GrId_band')  # for field 'leftList' type 'band'
    clearWell('sessionsGr_GrId')  # in lk_cur + stickers

    for gr, te in sessionsGr_GrId.items():
        toWell(te, 'sessionsGr_GrId', gr)
    for gr, te in sessionsGr_GrId_band.items():
        ls = [x.partition('|')[2] for x in sorted(te)]
        toSwell(ls, 'sessionsGr_GrId_band', gr)
    toWell(sorted(sessionsGr_All, key=lambda dc: dc.date_begin), 'sessionsGr_All')
    toWell(sorted(sessionsGrCommon, key=lambda dc: dc.title, reverse=True), 'sessionsGrCommon')

# *** *** ***


def createSessionSt():
    from nv.models import SessionSt

    studs = well('students_grId')
    if not studs:
        return

    tempSst = {}
    for sst in SessionSt.docs.values().all():
        tempSst[f"{sst['pref']}|{sst['sessiongr_id']}"] = getBody(sst)

    clearWell('other')
    sessionSt_idPr = {}
    sessionSt_sgrId = {}

    toWell(1, 'busy')
    saved = 0
    ggr = None

    def getSst(sgr, prf, stm, owner=None):
        nonlocal sessionSt_idPr, sessionSt_sgrId, nvGrId, saved, ggr
        dc = tempSst.get(f'{prf}|{sgr}')
        noPr = noGr = None
        if dc:
            if not owner:
                if dc.other_group:  # owner None - source gr
                    k = f'{dc.other_group}|{nvGrId}|{stm}'
                    other = well('other')
                    if k not in other:
                        other[k] = []
                    if prf not in other[k]:
                        other[k].append(prf)
            else:  # борьба с дублированием в подмененной группе
                if prf in sessionSt_idPr:
                    for sst in sessionSt_idPr[prf]:
                        if dc.pk == sst.pk:
                            noPr = True

                if sgr in sessionSt_sgrId:
                    for sst in sessionSt_sgrId[sgr]:
                        if dc.pk == sst.pk:
                            noGr = True
        elif ggr.status != 'active':  # не создавать сст для архивных групп
            return
        else:
            dcm = DC(dbAlias='nv_SessionSt')
            dc = dcm.doc = DC(
                pref=prf,
                sessiongr=sgr,
                status='active',
                owner=owner,
                allow_s=1,
                video_s=1,
            )

            sst = dcm.save()
            saved += 1
            if sst:
                dc.id = dc.pk = sst.id
                dc.sessiongr_id = dc.sessiongr
                tempSst[f'{prf}|{sgr}'] = dc
            else:
                err(f'pref={prf}, sessiongr={sgr}', cat='create SessionSt')
                return

        if not noPr:
            sessionSt_idPr[prf] = sessionSt_idPr.get(prf, [])
            sessionSt_idPr[prf].append(dc)

        if not noGr:
            sgr = str(sgr)

            sessionSt_sgrId[sgr] = sessionSt_sgrId.get(sgr, [])
            sessionSt_sgrId[sgr].append(dc)

    # ***

    for nvGrId, studArr in studs.items():  # studArr - массив студентов одной группы
        ggr = well('groups_groupId', nvGrId)
        if not ggr:
            continue

        # читаем все сессии группы
        for sgr in well('sessionsGr_GrId', nvGrId):
            if sgr.date_begin:  # у группы есть сессия с датой
                for stud in studArr:  # для этой сесс гр бежим по все студентам группы
                    getSst(sgr.pk, stud.id, sgr.sessiontmpl_id)  # False -проверить на подмену

    if well('other'):
        for k, prefArr in well('other').items():
            # ищем или создаем доп сессию для замененной группы
            # нужно найти ту же сессию для замененной группы
            other, owner, tmpl = k.split('|')
            for pref in prefArr:
                for sgr in well('sessionsGr_GrId', other):  # ищем в ohter-группе сессию с тем же шаблоном и датой начала
                    if sgr.sessiontmpl_id == tmpl and sgr.date_begin:
                        # если вызов для конкртеной группы, sessionSt_idPr пустой
                        sessionSt_idPr[pref] = sessionSt_idPr.get(pref) or well('sessionSt_idPr').get(pref, [])
                        sessionSt_sgrId[sgr.pk] = sessionSt_sgrId.get(sgr.pk) or well('sessionSt_sgrId').get(sgr.pk, [])
                        getSst(sgr.pk, pref, tmpl, owner)

    clearWell('sessionSt_idPr')
    clearWell('sessionSt_sgrId')

    for idPr, sessSt in sessionSt_idPr.items():
        toWell(sessSt, 'sessionSt_idPr', idPr)

    for idGr,sessSt in sessionSt_sgrId.items():
        toWell(sessSt, 'sessionSt_sgrId', idGr)

    toWell(0, 'busy')
    saved and snd(f'created: {saved}', cat='createSessionSt')

# *** *** ***


def loadGroups():
    from nv.models import NVGroup

    clearWell('groups_groupId')

    groups = []  # all groups
    allGroups = []  # для выбора группы в lbsd/lbmd
    commonGroups = []
    for group in NVGroup.docs.values().all():
        dc = getBody(group)

        if dc.commonGroups:
            commonGroups.append(f'{dc.title}|{dc.pk}')
        else:
            allGroups.append(f'{dc.title}|{dc.pk}')  # for droplist

        toWell(dc, 'groups_groupId', dc.pk)  # use in schedule and sgr
        groups.append(f'{dc.title}|{dc.pk}|{dc.status}')  # for views

    toSwell(sorted(allGroups, reverse=True), 'allGroups')
    toSwell(sorted(groups, reverse=True), 'groups')
    toSwell(sorted(commonGroups, reverse=True), 'commonGroups')

# *** *** ***


def loadSessionTmpl():
    from nv.models import SessionTmpl

    clearSwell('sessionTmpl_nve_band')  # msgBox добавить сесс

    clearWell('sessionTmpl_nve')  # стикеры + форма v_content
    clearWell('sessionTmpl_id')  # стикеры
    sessionTmpl_nve = {'all': []}  # all
    sessionTmpl_nve_band = {}  # msgBox добавить сесс
    for stmpl in SessionTmpl.docs.values().all():
        dc = getBody(stmpl)
        if not dc.nvEvent:
            err(f'dc.nvEvent empty. {dc.id}: {dc.title}', cat='loadSessionTmpl')
            continue
        toWell(dc, 'sessionTmpl_id', dc.pk)  # чтобы ссылки работали для удаленных stml
        if dc.status == 'deleted':
            continue

        sessionTmpl_nve[dc.nvEvent] = sessionTmpl_nve.get(dc.nvEvent,[])
        sessionTmpl_nve[dc.nvEvent].append(dc)
        sessionTmpl_nve['all'].append(dc)

        if dc.status == 'active':
            sessionTmpl_nve_band[dc.nvEvent] = sessionTmpl_nve_band.get(dc.nvEvent, [])
            sessionTmpl_nve_band[dc.nvEvent].append(f'{dc.title}|{dc.pk}')

    for cu,te in sessionTmpl_nve.items():
        toWell(sorted(te, key=lambda x: x.title), 'sessionTmpl_nve', cu)

    for cu,te in sessionTmpl_nve_band.items():
        toSwell(sorted(te), 'sessionTmpl_nve_band', cu)

# *** *** ***


def loadProfiles():
    from nv_c.models import Profile

    dpr = {}
    for k in swell('role'):
        dpr[k] = set()

    curators2 = set()
    lectors2 = set()
    student2 = set()
    tutors2 = set()
    alls = set()
    profiles = {}
    profByUserId = {}
    profilesByPhone = {}
    students_grId = {}
    more = []

    i = 0
    for prf in Profile.docs.values().all():
        i += 1
        dc = getBody(prf)

        for k in ['fest', 'training', 'invite']:
            if dc[k]:
                more.append(dc)
                break

        full_name = dc.full_name
        status = dc.status
        role = dc.role
        pk = dc.pk = dc.id
        phone = dc.phone
        fs = f'{full_name}|{pk}|{phone}|{dc.email}|{status}'
        alls.add(fs)
        profiles[pk] = dc

        if dc.user:
            profByUserId[dc.user] = dc  # for django login

        phone = cleanPhone(dc.phone.partition(',')[0].partition('\n')[0])
        if phone:
            profilesByPhone[phone] = dc  # for login via yandex

        for r in role.split('\n'):
            if r not in dpr:
                continue

            dpr[r].add(fs)

            if dc.status == 'active':
                if r == 'куратор':
                    curators2.add(f'{full_name}|{pk}')
                if r == 'преподаватель':
                    lectors2.add(f'{full_name}|{pk}')

            if not any(r == x for x in ['студент', 'гость', 'участник', 'выпускник']):
                dpr['сотрудник'].add(fs)
                tutors2.add(f'{full_name}|{pk}')

        # students_grId
        if 'студент' in role:
            if dc.status == 'active':
                student2.add(f'{full_name}|{pk}')

        groups = dc.student_groups
        if groups:
            for titleGr in groups.split('\n'):
                grId = titleGr.partition('|')[2]
                if grId:
                    students_grId[grId] = students_grId.get(grId, [])
                    students_grId[grId].append(dc)
        else:
            for gr in swell('allGroups'):  # f'{dc.title}|{dc.pk}'
                grT, _, grId = gr.partition('|')
                if grT == '_без группы':
                    students_grId[grId] = students_grId.get(grId, [])
                    students_grId[grId].append(dc)

    for k, v in dpr.items():
        toWell(sorted(v), k)

    toSwell(sorted(curators2), 'куратор2')
    toSwell(sorted(lectors2), 'преподаватель2')
    toSwell(sorted(student2), 'студент2')
    toSwell(sorted(tutors2), 'tutors2')

    toWell(sorted(alls), 'alls')
    toWell(profiles, 'profiles')
    toWell(profByUserId, 'profByUserId')
    toWell(profilesByPhone, 'profilesByPhone')

    clearWell('students_grId')  # for students by group
    for gr,stud in students_grId.items():
        toWell(sorted(stud,key=lambda dc: dc.full_name),'students_grId',gr)

    clearSwell('more')
    toSwell(more, 'more')

    snd(f'users: {i}', cat='all_users')

    # *** *** ***

def loadPayments():
    from nv.models import Payment

    payments_profile = {}
    payments = []
    for pay in Payment.docs.values().all():
        dc = getBody(pay)
        payments.append(dc)
        payments_profile[pay['pref']] = payments_profile.get(pay['pref'], [])
        payments_profile[pay['pref']].append(dc)

    toWell(sorted(payments, key=lambda dc: dc.PAY_DATE, reverse=True), 'payments')
    clearWell('payments_profile')
    for k, v in payments_profile.items():
        toWell(sorted(v, key=lambda dc: dc.PAY_DATE, reverse=True), 'payments_profile', k)


# *** *** ***


def loadLanding():
    from arm.tools.dbToolkit.Book import allFromDB
    landingByPage = {}
    landingByKey = {}
    landing = []
    for dc in allFromDB('draft'):
        if dc.status != 'deleted':
            landing.append(dc)
            if dc.pageName:
                landingByPage[dc.pageName.lower()] = dc
            if dc.key:
                k = dc.key.lower()
                landingByKey[k] = landingByKey.get(k, [])
                landingByKey[k].append(dc)

    toWell(landingByPage, 'landingByPage')
    toWell(landingByKey, 'landingByKey')
    toWell(landing, 'landing')

