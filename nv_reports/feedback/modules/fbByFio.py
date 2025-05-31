from arm.tools.loadWell import loadWell
from arm.tools.DC import DC, well
from arm.api.forms.formTools import labField, style, label, _div, _field, gridStyle, docTitle
from arm.tools.first import err, snd

from nv_reports.misc.sessGr import findEqSGr, getFioList

import os
import json

import django

import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arm.settings')
django.setup()

def main(m):
    fioList = getFioList(m)
    findEqSGr(m, fioList)
    ass(fioList)

    htmlList = []
    for fio, ls in sorted(fioList.items()):
        # if 'Гончарова Лилия Амировна' not in fio:
        #     continue
        resultArr = []
        arr = []
        for sgr in ls:
            arr.append(dict(gr=f'{sgr.grTitle}', stm=f'{sgr.sessTitle}', balls=f'{sgr.balls or "z"}'))

        df = pd.DataFrame(arr)
        pivot_table = df.pivot(index='stm', columns='gr', values='balls').fillna('-')

        resultArr.append([''] + pivot_table.columns.tolist())
        os = ni = 0
        for i in range(len(pivot_table)):
            row = pivot_table.iloc[i]
            ni += 1
            if any([s not in ['-', 'z', ] for s in row.tolist()]):
                os += 1
            resultArr.append([row.name] + row.tolist())

        # таблица создана, делает html:

        fio = fio.partition("|")[0]
        # 1 строка отчета
        rows = [_div(fio, className='fio')]

        # 2 строка отчета (комментарий и пояснения)
        rows.append(_div(f'''<<C+Обратная связь ({m.addList})>>
ОС: - количество проголосавших из общего кол-ва
Б: - сумма баллов. Ср: - средний балл (Б/ОС)''', ckassName='comment', br=1, s2=1))

        grid = '250px' + (' 150px' * (len(resultArr[0]) - 1))

        # заголовки столбцов
        rows.append(_div(**gridStyle(grid), className='header', children=[ _div(d) for d in resultArr[0]]))

        # таблица
        for k in resultArr[1:]:
            rows.append(_div(**gridStyle(grid), className='row', children=[ _div(d, br=1) for d in k]))

        ngr = len(resultArr[0]) - 1
        # заголовок документа в виде
        title = f'{fio}. Гр:{ngr} Сесс:{ni} ОС:{os}'

        html = DC(log=m.log, title=title)
        html.main = json.dumps([_div(className='first', children=rows)], ensure_ascii=False)
        html.jsCss = 'misc/tables.css'
        htmlList.append(html)
        # break

    return htmlList

# *** *** ***


def ass(fioList):
    for lectorsArr in fioList.values():
        for sgr in lectorsArr:
            students = studBalls = balls = 0
            # в каждую сессию группы добавляем сумму балов
            for dc in well('sessionSt_sgrId', sgr.pk):  # all sst for this sgr
                students += 1
                ballslOne = 0
                for x in dc.keys():
                    if x.startswith('ASSLEC') and dc[x]:
                        ballslOne += int(dc[x], 10)

                if ballslOne:  # студен что-то оценил
                    studBalls += 1
                    balls += ballslOne

            if balls:
                # ss = f'Оценили: {studBalls} из {students}. Баллов: {balls}. Среднее: {balls/studBalls}'
                # print(ss)
                sgr.balls = f'ОС: {studBalls} из {students}\nБ: {balls}. Ср: {balls/studBalls:.2f}'

        # добавляем лектору сессию группы, в которой уже есть данные по ос


# *** *** ***


        # dc.main = _div(**gridStyle('100px 1fr'), children=[
        #             label(k),
        #             _div(v)
        #         ])

# *** *** ***


if __name__ == "__main__":
    loadWell('all')
    _m = DC(firstList='Куратор', addList='Сессии')
    main(_m)
    print(_m.log)

