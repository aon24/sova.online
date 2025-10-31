'''
Created on 2022

@author: aon

'''


def blank3mmm(scale):
    x, y, z = 400, 600, 270

    return dict(
        rect=dict(left=0, top=0, width=0, height=0),
        className='is3d',
        tuning=dict(
            mmm='rooms',
            scale3d=scale,
            is3dX=x, is3dY=y, is3dZ=z,  # размеры стен и пола (это не rect !!!)
            sweep=45,  # нклон стен
            angleHide=45,  # угол скрытия
            # rotate3Z=0, rotate3X=0,  # поворот наклон
            rotate3Z=30, rotate3X=75,  # поворот наклон
            coverOn=1,  # показать потолок
            bb3d=0,  # 3д-стены-мебель-++
            shadowColor3='#a17c3c', shadowW3=35, shadowR3=25,  # тень
            w3=20,
            fixed=1,
        )
    )

# *** *** ***


# b1 = '#ddeeff70'
b1 = '#b1bdc9' '70'  # b7d2ed70'


def blank3d(key):
    return dict(
        boxIndex=0,  # pageBox
        tuning={'screen': 100},  # screen - номер экрана по умолчанию (100: рут=100 первый блок=1000
        boxes=[
            # boxIndex = 100 rootBox
            dict(
                boxIndex=100,
                tuning=dict(
                    backgroundColor=b1,
                    bgStyle='color',
                    fixed=1,
                ),
                rect=dict(left=0, top=0, width=4000, height=3000),
                boxes=[
                    dict(boxIndex=1000,  # - главный бокс для страницы
                         rect=dict(left=100, top=100, width=1200, height=700),
                         tuning=dict(
                            bgStyle='color', backgroundColor='#fff',
                            border='borEQ', borderWidth=3, borderRadius=7, borderColor='#aaa',
                            borderRadiusMetric=1,
                            # noIcons=1,
                            # overflow='auto',
                            fixed=1,
                            k1000='rooms'
                                     ),
                         boxes=[
                            dict(
                                # boxIndex=1001,
                                rect=dict(left=400, top=300, width=0, height=0),
                                tuning={},
                                boxes=[blank3mmm(1)]
                                )] if key == '3d+' else []
                         )]
            ),

            # boxIndex = 200 rootBox
            smartPhone(200, 480, 960, key),
        ]
    )

# *** *** ***


[lim, width] = [0, 0]


def row(part, rootIndex, add):
    global lim

    r = {'boxIndex': rootIndex + add, 'rect': {'height': part}}

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

# *** ** ***


def smartPhone(rootIndex, w, height, key):  # dim - масштаб pagePlus
    global lim, width

    [lim, width] = [0, w];

    r = 20
    if rootIndex == 200:
        parts = [96, 800, 64]
        cells = [
            row(parts[0], rootIndex, 1),  # boxIndex = 101 or 201 or 301...901
            row(parts[1], rootIndex, 2),
            row(parts[2], rootIndex, 3)
        ]
        top = parts[0]
        h = parts[1]
    else:
        top = 0
        h = height
        cells = []

    return dict(# root для данного экрана
        declare=f'{width}x{height}',
        boxIndex=rootIndex,  # boxIndex = 100, 200,... 900
        type='rows' if cells else None,
        tuning=dict(
            backgroundColorWP=b1,
            bgStyleWP='color',

            backgroundColor='#ddeeff70',
            bgStyle='color',
            border='borEQ',
            borderWidth=r,
            borderColor='#4488aa30',
            borderRadius=40,
            borderRadiusMetric=1,
            insideOnly=1,
            position='relative',
            margin='auto',
            phoneContur=1,
        ),
        cells=cells,
        # 3 служебных ряда для смартфона: отступ сверху 16мм, экран 124мм, отступ снизу 10мм (Redmi Note 9)

        boxes=[
            dict(
                boxIndex=rootIndex * 10,  # boxIndex = 2000 - главный бокс для страницы
                rect=dict(left=0, top=top, width=width, height=h),
                tuning=dict(fixed=1, backgroundColor='#ffffff', bgStyle='color'),

                boxes=[dict(# boxIndex=2001,
                    rect=dict(left=150, top=300, width=0, height=0),
                    tuning={'noIcons': 1},
                    boxes=[blank3mmm(0.5)]
                )] if key == '3d+' else []
            )],

        rect=dict(width=width + 2 * r, height=(lim or h) + 2 * r, left=0, top=0),
    )

