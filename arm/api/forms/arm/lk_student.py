'''
Created on 2024

@author: aon24
'''

from arm.tools.DC import well, config
from arm.api.forms.formTools import _tabNew, _btnEdit, _field, style, _div, gridStyle
from arm.api.forms.lk_tools import getSessStByProfId, sstButtons, rightBtnLK3, btnLogout, btnSetting, btnProfile

from datetime import datetime, timedelta

# *** *** ***


def studentTabNew(arm):
    reports = _div(children=[
        _field('tables', 'band', ['Платежи', 'Программа', 'Хвосты'], **style(margin='auto', display='table', width='auto')),
        _div(**style(border='0 solid #036', padding=5, borderWidth='2px 0 0 0', overflow='auto'),
            children=[_field('dataTable', 'json')]
        )
    ])
    contacts = _div(config.contacts, **style(height='auto', overflow='auto', padding=10), br=1)
    return [
        ('Расписание', studentSheet(arm), 105),
        ('Отчеты', reports, 80),
        ('Контакты', contacts, 85),
    ]


# *** *** ***


def showLKStudent(arm):
    return _div(
        className='page51',
        children=[
            btnLogout,
            btnSetting,

            _div(**style(maxWidth=1200, margin='auto'),
                children=[
                    _div(className='propfile', children=[btnProfile]),
                    _div(**style(overflow='hidden', height='calc(100vh - 32px)'),
                        children=[_tabNew('lks_Table_FD', tabs=studentTabNew(arm))]
                    )
            ])
    ])

# *** *** ***

def lk_student(arm):
    return _div(**style(height='100%', paddingTop=5),  # background='url("/image/nvbg.jpeg")'),
        children=[
            _div(**style(width=250, margin='auto', boxShadow='0px 17px 5px 20px #88aa0080')),
            _tabNew(xName='lks_Table_FD', tabs=studentTabNew(arm), center=True)
    ])

# *** *** ***


def studentSheet(arm):
    arm.leftList = arm.leftWidth = arm.upField = None
    arm.viewbar = arm.makeViewbar(
        **gridStyle('1px 1fr', borderWidth='0 0 2px 0', background='transparent'),
        rightBtn=rightBtnLK3(),
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

    forSort = []

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
        row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto auto auto auto auto auto'),
            children=[title, *sstButtons(sst, sgr), _btnEdit('cmdEdit3', pk)])

        forSort.append((sgr.title, [pk, row]))

    forSort.sort(key=lambda t: t[0])
    mainDocs = [x[1] for x in forSort]

    return {'mainDocs': mainDocs, 'refsDocs': None}

# *** *** ***


