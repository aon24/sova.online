'''
Created on 2024

@author: aon24
'''

from arm.tools.DC import well
from arm.api.forms.formTools import _tabNew, _btnEdit, _field, style, _div, gridStyle
from arm.api.forms.lk_tools import showLK, getSessStByProfId, sstButtons, rightBtnLK

from datetime import datetime, timedelta

# *** *** ***


def lk_student(arm, dcUK):
    tab = _div(children=[
        _field('tables', 'band', ['Платежи', 'Программа', 'Хвосты'], **style(margin='auto', display='table', width='auto')),
        _div(**style(border='0 solid #048', padding=5, borderWidth='2px 0 0 0', overflow='auto'),
            children=[_field('dataTable', 'json')]
        )
    ])
    table = [
            ('Расписание', studentSheet(arm), 105),
            ('Отчеты', tab, 80),
            ('Контакты', contacts(dcUK), 85),
    ]

    if dcUK._role == 'студент':
        return showLK(table, dcUK.fullName, width=110, ah=6)
    else:
        return _div(**style(height='100%', paddingTop=10),
            children=[_tabNew(xName='lks_Table_FD', tabs=table)
        ])

# *** *** ***

# *** *** ***


def studentSheet(arm):
    arm.leftList = arm.leftWidth = arm.upField = None
    arm.viewbar = arm.makeViewbar(
            **gridStyle('1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
            rightBtn=rightBtnLK('3'),
        )

    url = '/api/getData?form=arm&cmd=getSelected3&showLK_id={showLK_id}&status={status3}&plan={plan3}'
    previewUrl = ''  # 'dbAlias=nv_SessionSt'
    arm.mainList = _div(**style(height='100%'), children=[
        _field('mainList3', 'view', name='mainList3', limit=100000, url=url, previewUrl=previewUrl, noMount=1),
        _field('showCourse3', 'json', **style(height='100%'), name='showCL3'),
    ])
    sh = arm.sham()

    return sh

# *** *** ***


def getViewStudent(dcUK):
    sessStArr = getSessStByProfId(dcUK)[0]

    mainDocs = []

    days = 1 if dcUK.plan == '0' else 100000  # не показ эскизы через 1 день после оконч or isEmpty
    yesterday = datetime.now() - timedelta(days=days)
    last = yesterday.strftime("%Y-%m-%d")

    for sst in sessStArr:
        if sst.form == 'SessionGr':
            sgr = sst
            dateEnd = sgr.date_end or sgr.date_begin
            if dateEnd < last:
                continue

            color = '#55f'
            s = 'Общая группа'
        else:
            sgr = well('sessionGr_Id', sst.SESSIONGR_ID)
            dateEnd = sgr.date_end or sgr.date_begin
            if dateEnd < last:
                continue

            if sst.other_group:
                color = '#888'
                s = f"(подмена в {well('groups_groupId', sst.other_group).title})"
            elif sst.owner:
                color = '#f55'
                s = f"(подмена из {well('groups_groupId', sst.owner).title})"
            else:
                color = '#000'
                s = ''


        grTitle = well('groups_groupId', sgr.nvgroup_id).title
        title = _div(f"{sgr.title} ({grTitle}){sst.form}\n{sgr.d2}({sgr.duration}) {s}",
            s2=1, br=1, **style(letterSpacing=1, paddingLeft=2, color=color))


        pk = f"unid={sst.id}&form={sst.form or 'SessionSt'}"
        row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto auto auto'),
            children=[title, *sstButtons(sst, sgr), _btnEdit('cmdEdit3', pk)])

        mainDocs.append([pk,row])

    return {'mainDocs': mainDocs, 'refsDocs': None}

# *** *** ***


def contacts(dcUK):
    return _div('''
<<C+ООО "Институт психологического консультирования "Новый Век">>
199004, Санкт-Петербург, 6-ая линия ВО., д. 23, литер А, помещение 14Н
Телефон: (812) 329-08-02, +7 (921) 778-65-85
Электронная почта: info@institutnv.ru
Фактический адрес: 199004, Санкт-Петербург, 6-ая линия ВО., д. 23, 3 и 4 этаж

ИНН/КПП 7801534222 / 780101001
Расчетный счет: 40702810303260005823
в ФИЛИАЛЕ «Центральный» Банка ВТБ  (ПАО)
БИК 044525411
Кор. счет: 30101810145250000411
''', br=1)

# *** *** ***
