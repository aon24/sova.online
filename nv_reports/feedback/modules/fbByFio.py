from arm.tools.loadWell import loadWell
from arm.tools.DC import DC, well
from arm.api.forms.formTools import style, _div, gridStyle
from arm.tools.first import err

from nv_reports.misc.sessGr import findEqSGr, getFioList

import os
import json

import django

import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arm.settings')
django.setup()


def main(m):
    fioList = getFioList(m)  # словарь
    findEqSGr(m, fioList)  # ищет дубли и добавляет в sgr.sessTitle += f'-{nDubl}'
    ass(fioList)  # бежит по все сессГр, для каждой выюирает все сессСт и пишет в сессГр balls

    gridString = f'1fr{" 70px"*6}'
    htmlList = []
    for fio, ls in sorted(fioList.items(), reverse=True):
        # if 'Гончарова Лилия Амировна' not in fio:
        #     continue
        resultArr = []
        arr = []
        ballslOne = studBalls1 = ballslTwo = studBalls2 = mansBalls = mans = 0

        for sgr in ls:
            # if fio == 'Анисимова Ирина Владимировна 2025-5/Веч':
            #     print('--------------------------------------', sgr.mans)
            #     for dc in well('sessionSt_sgrId', sgr.id):
            #         print(well('profiles', dc.pref).full_name, dc.assLec1)

            mans = sgr.mans

            if sgr.mansBalls:
                mansBalls += sgr.mansBalls

            if sgr.ballslOne:
                ballslOne += sgr.ballslOne
            if sgr.ballslTwo:
                ballslTwo += sgr.ballslTwo
            if sgr.studBalls1:
                studBalls1 += sgr.studBalls1
                ev1 = f'{sgr.ballslOne/sgr.studBalls1:.2f}'
            else:
                ev1 = '-'
            if sgr.studBalls2:
                studBalls2 += sgr.studBalls2
                ev2 = f'{sgr.ballslTwo/sgr.studBalls2:.2f}'
            else:
                ev2 = '-'

            arr.append(dict(gr=f'{sgr.grTitle}', stm=f'{sgr.sessTitle}',
                            balls=[f'{sgr.d2 or ""}', str(mans), str(sgr.mansSignup),
                                   str(sgr.mansBalls), ev1, ev2]))

        # заголовок документа в виде
        if studBalls1:
            even1 = f'{ballslOne/studBalls1:.2f}'
        else:
            even1 = '-'
        if studBalls2:
            even2 = f'{ballslTwo/studBalls2:.2f}'
        else:
            even2 = '-'

        title = _div(**gridStyle(gridString, marginLeft=20, placeItems='center'), className='rCell', children=[
            _div(fio, **style(justifySelf='start')),
            _div(f'{len(ls)}'),
            _div(f'{mans}'),  # всего людей
            _div(f'{sgr.mansSignup}'),  # сколько зарегились
            _div(f'{mansBalls}'),  # всего OS
            _div(f'{even1}'),  # even
            _div(f'{even2}'),  # even
        ])

        # sgr.mans = len(well('sessionSt_sgrId', sgr.id))  # всего людей
        # sgr.mansBalls = studBalls  # сколько ОС
        # sgr.mansSignup = signup  # сколько зарегились
        # sgr.ballslOne = ballslOne # сумма балов 1
        # sgr.studBalls1 = studBalls1 # колич студне для балоов 1
        # sgr.ballslTwo = ballslTwo# сумма балов 2
        # sgr.studBalls2 = studBalls2 # колич студне для балоов 2

        df = pd.DataFrame(arr)
        pivot_table = df.pivot(index='stm', columns='gr', values='balls').fillna('-')

        resultArr.append([''] + pivot_table.columns.tolist())
        ni = 0
        for i in range(len(pivot_table)):
            row = pivot_table.iloc[i]
            ni += 1
            resultArr.append([row.name] + row.tolist())

        # таблица создана, делает html:

        # 1 строка отчета
        rows = [_div(fio, className='fio')]

        # 2 строка отчета (комментарий и пояснения)
        rows.append(_div(f'''<<C+Обратная связь ({m.firstList})>>''', className='comment', br=1, s2=1))

        grid = '1fr' + (' 70px' * 5)

        # заголовки столбцов
        rows.append(_div(
            **gridStyle(grid), className='header',
            children=[_div('сессия'),
                      _div('студ.'),  # всего людей
                      _div('зарег.'),  # сколько зарегились
                      _div('дали ос'),  # всего OS
                      _div('к1-8'),  # even
                      _div('к9-12'),  # even
                      ]))

        # таблица
        for k in resultArr[1:]:
            values = [_div(f'{k[0]}\n{k[1][0]}', br=1)] + [_div(d, br=1) for d in k[1][1:]]
            rows.append(_div(**gridStyle(grid), className='row', children=values))

        # resultArr[0] - заголовок таблицы
        html = DC(log=m.log, title=title)
        html.main = json.dumps([_div(className='first', children=rows)], ensure_ascii=False)
        html.jsCss = 'misc/tables.css'
        htmlList.append(html)

    title = _div(**gridStyle(gridString, marginLeft=20, font='bold 14px Verdana', color='#048',
                 border='0 solid #048', borderBottomWidth=1, placeItems='center'),
                 children=[
                    _div(f'{m.firstList} (группа)'),
                    _div('сессий'),
                    _div('студ.'),  # всего людей
                    _div('зарег.'),  # сколько зарегились
                    _div('дали ос'),  # всего OS
                    _div('к1-8'),  # even
                    _div('к9-12'),  # even
            ])
    htmlList.append(DC(log=m.log, title=title, jsCss='misc/tables.css'))

    return htmlList

# *** *** ***


def ass(fioList):
    for lectorsArr in fioList.values():
        for sgr in lectorsArr:
            students = studBalls = studBalls1 = studBalls2 = ballslOne = ballslTwo = signup = 0
            # в каждую сессию группы добавляем сумму балов
            for dc in well('sessionSt_sgrId', sgr.id):  # all sst for this sgr
                prof = well('profiles', dc.pref)
                if prof.status != 'active':
                    continue

                signup += 1 if prof.user_id else 0
                students += 1
                stb = 0  # студен не оценил
                for x in dc.keys():
                    if x.startswith('ASSLEC') and dc[x] and not x.startswith('ASSLECTEXT'):
                        try:
                            stb = 1  # студен что-то оценил
                            n = int(x.partition('ASSLEC')[2], 10)
                            if n < 9:
                                studBalls1 += 1
                                ballslOne += int(dc[x], 10)
                            else:
                                studBalls2 += 1
                                ballslTwo += int(dc[x], 10)
                        except Exception:
                            err(f'invalid literal for int\n{dc}', cat='fbByFio.py:ass')

                studBalls += stb

            # if balls:
                # ss = f'Оценили: {studBalls} из {students}. Баллов: {balls}. Среднее: {balls/studBalls}'
                # print(ss)
                # sgr.balls = f'ОС: {studBalls} из {students}\nБ: {balls}. Ср: {balls/studBalls:.2f}'

            sgr.mans = students  # всего людей
            sgr.mansBalls = studBalls  # сколько ОС
            sgr.mansSignup = signup  # сколько зарегились
            sgr.ballslOne = ballslOne  # сумма балов 1
            sgr.studBalls1 = studBalls1  # колич студне для балоов 1
            sgr.ballslTwo = ballslTwo  # сумма балов 2
            sgr.studBalls2 = studBalls2  # колич студне для балоов 2

        # добавляем лектору сессию группы, в которой уже есть данные по ос


# *** *** ***

        #  dc.main = _div(**gridStyle('100px 1fr'), children=[
        #             label(k),
        #             _div(v)
        #         ])

# *** *** ***


if __name__ == "__main__":
    loadWell('all')
    _m = DC(firstList='Куратор', addList='Сессии', dt1='2025-04-01', dt2='2025-06-19')
    main(_m)
    print(_m.log)
