'''
Created on 2025
@author: aon24
'''
from arm.tools.DC import DC, well


def getFioList(m):
    if 'Куратор' in m.firstList:
        key = 'curator'
    if 'Препод' in m.firstList:
        key = 'lector'
    event = m.addList

    lectors = {}

    # шаг 1. Создаем словарь {fio: [sgr1,..]}
    for sessGr in well('sessionsGr_All'):
        if sessGr.status != 'active':
            continue
        tmpl = well('sessionTmpl_id', sessGr.SESSIONTMPL)
        if tmpl.status != 'active':
            continue
        nvGr = well("groups_groupId", sessGr.nvGroup)
        if nvGr.status != 'active':
            continue
        e = well('eventsByCode', tmpl.nvEvent)
        if event != 'Все' and event != e:
            continue

        dt1 = sessGr.date_begin
        dt2 = sessGr.date_end
        if m.dt1 and dt1 and (m.dt1 > dt1 or (m.dt2 and dt2 and m.dt2 < dt2)):
            continue

        sgr = DC(sessGr)  # copy all fields

        # добавляем лектору сессию группы
        fio = sgr[key].replace('\n', ' - ') or '<???>'
        if sgr[key]:
            sgr.grTitle = nvGr.title
            sgr.sessTitle = tmpl.title
            lectors[fio] = lectors.get(fio, [])
            lectors[fio].append(sgr)
        else:
            m.log += f'\nСессии не созданы: {fio} гр:{nvGr.title} сесс:{tmpl.title}'

    return lectors

# *** *** ***


def findEqSGr(m, fioList):
    for fio, ls in fioList.items():
        nDubl = 0
        while True:
            dubl = False
            arr = []
            for sgr in ls:
                s = f'{fio} gr={sgr.grTitle}, sgr={sgr.sessTitle}'
                try:
                    ind = arr.index(s)
                    dubl = True
                    nDubl += 1
                    sgr.sessTitle += f'-{nDubl}'
                    ss = f'{s}-{nDubl} {sgr.date_begin}'
                    m.log += '\n Дублирование:' + ss
                    arr[ind] = ss
                    nDubl += 1
                    ss = f'{s}-{nDubl} {sgr.date_begin}'
                    m.log += '\n Дублирование:' + ss
                    arr.append(ss)
                    break
                except:
                    arr.append(s)

            if not dubl:
                break

