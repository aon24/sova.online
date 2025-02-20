'''
Created on 14 мар. 2021 г.

@author: aon
'''

from .mmm import blank3d

import json


def blankScreens(key):
    bi = 1001

    [lim, width] = [0, 0]

    def row(part, rootIndex, add):
        global lim, width

        r = {'boxIndex': rootIndex + add, 'rect': {'height': part} }

        if add == 2:
            r['tuning'] = dict(bgStyle='color', backgroundColor='#fffFFF40',
                border='borEQ', borderWidth=1, borderColor='#aaa')

        elif add == 3:  # кнопки на нижней части
            centr = width / 2
            rad = 25
            t = (part - rad) / 2
            r['boxes'] = [
                {   'rect': dict(top=t, left=centr - 4 * rad, height=rad, width=rad),
                    'tuning': dict(bgStyle='color', backgroundColor='#00000060'),
                    'boxIndex': rootIndex + add + 1
                },
                {   'rect': dict(top=t, left=centr - (rad / 2), height=rad, width=rad),
                    'tuning': dict(bgStyle='color', backgroundColor='#00000060',
                       border='borEQ', borderWidth=2, borderRadius=50, borderColor='#ffffff',
                       shadow='outside', shadowX=0, shadowY=0, shadowR=0, shadowW=2, shadowColor='#00000080'),

                    'boxIndex': rootIndex + add + 2
                },
                {   'rect': dict(top=t - 1, left=centr + 2.5 * rad, height=rad, width=rad),
                    'tuning': dict(
                       border='borNE',
                       borderRightWidth=rad / 2 + 1, borderRightColor='#00000060',
                       borderTopWidth=rad / 2,
                       borderBottomWidth=rad / 2,
                    ),
                    'boxIndex': rootIndex + add + 3
                },
            ]

        lim += r['rect']['height']
        return r

    def smartPhone(rootIndex, width, height, key):  # dim - масштаб pagePlus
        return dict(# root для данного экрана
            boxIndex=rootIndex,  # boxIndex = 100, 200,... 900
            tuning=dict(fixed=1),
            rect=dict(left=0, top=0, width=4000, height=3000),

            boxes=[
                dict(
                    boxIndex=rootIndex * 10,  # - главный бокс для страницы
                    rect=dict(left=400, top=10, width=width, height=height),
                    tuning=dict(bgStyle='color', backgroundColor='#fff',
                        border='borEQ', borderWidth=3, borderRadius=7, borderColor='#aaa',
                        borderRadiusMetric=1,
                        fixed=1,
                    )
            )]
        )

    def blank2d():
        return dict(
            boxIndex=0,
            tuning={'margin': 'auto', 'contur': 1, 'screen': 100},  # screen - номер экрана по умолчанию (100: рут=100 первый блок=1000
            boxes=[
                smartPhone(100, 480, 960, key),  # rootIndex = 100
                smartPhone(200, 600, 400, key),  # rootIndex = 200
                smartPhone(300, 1200, 960, key) ]  # + [smartPhone(i, 600, 400, 3) for i in range(400, 1000, 100)]
        )

    # *** *** ***
    # *** *** ***
    # *** *** ***

    # print(_blank3d['boxes'][0]['boxes'][0]['boxes'][0])

    # tuning.screen задает, какой режим выбрать. screen=0 - выбрать smartPhone(100,..) screen=1 - выбрать smartPhone(200,
    # boxIndex == 0 - служебный блок. Может содержать несколько страниц. Выбранная страница в переменной tuning.screen
    # boxIndex == 100 or 200 or 300 ... or 900 - root для данной страницы: 100 - smartPhone, 200 - монитор...)

    # *** *** ***
    # *** *** ***
    # *** *** ***

    ''' MMM '''
    # *** *** ***
    # *** *** ***
    # *** *** ***

    ''' RETURN '''
    # *** *** ***
    # *** *** ***
    # *** *** ***

    if key == '3d+' or key == '3d':
        b = blank3d(key)
    else:
        b = blank2d()
    return json.dumps(b, ensure_ascii=False)

