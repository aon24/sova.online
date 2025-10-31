'''
Created on 2025

@author: aon24
'''
from arm.api.forms.formTools import style, _div, gridStyle
from arm.tools.DC import well
# from arm.tools.first import err, snd

titleStyle = dict(margin='5px 0', border='0 solid #aaa', borderBottomWidth=2)

# *** *** ***


def groupReview(dcUK):
    titles = dict(
        allow_s='ДОПУСКУ',
        was_s='ПОСЕЩАЕМОСТИ',
        pay_s='ОПЛАТЕ',
        os_s='ОБР. СВЯЗИ',
        esse_s='ЭССЕ',
        consultant_s='КОНСУЛЬТАНТУ',
    )
    title = _div(f"""Сводка по <<C+{titles.get(dcUK.jobName)}>> для группы {well('groups_groupId', dcUK.nvGroup).title}
с {dcUK.D('dt1')} по {dcUK.D('dt2')}""", style=titleStyle, br=1)

    allSst = {}
    ls = []
    # 1. Отобрали сессии группы за период, создали dict всех сст по id сгр
    for sgr in well('sessionsGr_GrId', dcUK.nvGroup):
        if (sgr.date_end or sgr.date_begin) >= dcUK.dt1 and sgr.date_begin <= (dcUK.dt2 or '99'):
            if dcUK.filter == 'Sess' and sgr.nvEvent != '1':
                continue
            if dcUK.filter == 'Pr' and sgr.nvEvent not in ['P', 'P1', 'P2']:
                continue
            if dcUK.filter == 'L' and sgr.nvEvent not in ['L', 'CL']:
                continue
            allSst[sgr.id] = well('sessionSt_sgrId', sgr.id)
            ls.append(sgr)

    # ось х: сессии группу по порядку
    sortedSgr = [sgr.id for sgr in sorted(ls, key=lambda x: x.date_begin)]
    rows = len(sortedSgr)

    # 2. для каждого юзера создаем словарь его сессий , ключ - sgrId
    sstByUsers = {}
    for sgr, sstArr in allSst.items():
        for sst in sstArr:
            sstByUsers[sst.pref] = sstByUsers.get(sst.pref, {})
            sstByUsers[sst.pref][sgr] = sst

    # make header
    gridStr = f'auto 70px {" 20px"*rows}'
    ls = [_div('ФИО', className='review-left-gr', **style(textAlign='center', padding=25)),
          _div('Отмечено', **style(textAlign='center', padding=25, writingMode='vertical-lr'))
          ]
    for i, sgrId in enumerate(sortedSgr):
        sgr = well('sessionGr_Id', sgrId)
        color = '#fff' if i % 2 else '#f0fff0'
        ls.append(_div(f'{sgr.d2[:5]}. {sgr.title}', **style(background=color), className='headerStyle'))

    header = _div(**gridStyle(gridStr), children=ls)

    # make body
    body = []
    for pref, dictSst in sstByUsers.items():
        fi, _, na = well('profiles', pref).full_Name.partition(' ')
        ls = [_div(f'{fi} {na[0]}.', className='review-left-gr')]

        gut = 0
        for i, sgr in enumerate(sortedSgr):
            userSst = dictSst.get(sgr)  # вообщето сст обязана быть, но на всяк случ гет()
            color = '#fff' if i % 2 else '#f0fff0'

            if userSst:
                s = ''
                if dcUK.jobName != 'os_s':
                    if userSst[dcUK.jobName]:
                        s = '✅'
                        gut += 1
                else:
                    if any([userSst[x] for x in userSst.keys() if x.startswith('ASSLEC')]):
                        s = '✅'
                        gut += 1
                ls.append(_div(s, **style(background=color)))
            else:
                ls.append('❌', **style(background=color))
        ls.insert(1, _div(f'{gut} ({rows})', **style(textAlign='center')))
        body.append(_div(**gridStyle(gridStr), children=ls))

    return _div(className='review', children=[title, header, *body])

# *** *** ***


def studentReview(dcUK):
    fio, _, pref = dcUK.student.partition('|')
    title = _div(f"""<<C+{fio}>> ({well('groups_groupId', dcUK.nvGroup).title})
с {dcUK.D('dt1')} по {dcUK.D('dt2')}""", style=titleStyle, br=1)

    allows = ['Допуск', 'Был', 'Оплатеа', 'Обр. связь', 'Эссе', 'Консультант', ]
    rows = len(allows)

    gridStr = f"auto {(' 20px')*rows}"

    # make body
    body = []
    userSstArr = well('sessionSt_idPr', pref)

    ls = []
    gut = [0, 0, 0, 0, 0, 0]
    i = 0
    for sst in userSstArr:
        sgr = well('sessionGr_Id', sst.SESSIONGR_ID)
        if not ((sgr.date_end or sgr.date_begin) >= dcUK.dt1 and sgr.date_begin <= (dcUK.dt2 or '99')):
            continue
        if dcUK.filter == 'Sess' and sgr.nvEvent != '1':
            continue
        if dcUK.filter == 'Pr' and sgr.nvEvent not in ['P', 'P1', 'P2']:
            continue
        if dcUK.filter == 'L' and sgr.nvEvent not in ['L', 'CL']:
            continue

        i += 1
        color = '#fff' if i % 2 else '#f0fff0'
        ls.append(_div(f'{sgr.d2[:5]}. {sgr.title}', className='review-left-st', **style(background=color)))
        s = ''  # Допуск
        if sst.allow_s:
            s = '✅'
            gut[0] += 1
        ls.append(_div(s, **style(background=color)))

        s = ''  # Был
        if sst.was_s:
            s = '✅'
            gut[1] += 1
        ls.append(_div(s, **style(background=color)))

        s = ''  # 'Оплата
        if sst.pay_s:
            s = '✅'
            gut[2] += 1
        ls.append(_div(s, **style(background=color)))

        s = ''  # Обр.св.
        if any([sst[x] for x in sst.keys() if x.startswith('ASSLEC')]):
            s = '✅'
            gut[3] += 1
        ls.append(_div(s, **style(background=color)))

        s = ''  # Эссе
        if sst.esse_s:
            s = '✅'
            gut[4] += 1
        ls.append(_div(s, **style(background=color)))
        s = ''  # К-т
        if sst.consultant_s:
            s = '✅'
            gut[5] += 1
        ls.append(_div(s, **style(background=color)))
    body.append(_div(**gridStyle(gridStr), children=ls))

    # make header
    ls = [_div(className='review-left-st')]
    for i, allow in enumerate(allows):
        ls.append(_div(f'{allow}: {gut[i]} ({rows})', className='headerStyle'))
    header = _div(**gridStyle(gridStr), children=ls)

    return _div(className='review', children=[title, header, *body])

# *** *** ***


def main(dcUK):
    if dcUK.student:
        return studentReview(dcUK)
    else:
        return groupReview(dcUK)

# *** *** ***
