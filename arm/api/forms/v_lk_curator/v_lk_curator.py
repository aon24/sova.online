# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
'''
from arm.tools.first import err
from arm.tools.DC import well, swell, DC, toWell
from arm.tools.loadWell import loadWell
from arm.api.forms.formTools import style, _div, _btnD, _field, _btnEdit, _btnPref, gridStyle
from arm.api.forms.classPage import Page
from arm.tools.dbToolkit.DJ import docFromDB
from arm.api.forms.toolbars import toolbar
from arm.api.forms.sstButtons import sstButtons

from django.http import HttpResponse

import json

# *** *** ***


class v_lk_curator(Page):
    '''
    список сессий студентов для конкретоной sGr
    Установка/сброс "Д-З-Р-V" для выделенных студней
    Открывается из лк куратора по кнопке слева "номер группы"(под * * *)
    Слева список сессий, справа студенты
    '''
    dbAlias = 'nv_SessionSt'
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/v_lk_curator/v_lk_curator.js']
        self.leftWidth = 150

        super().__init__(request)

    def getData(self, dcUK):
        if not (dcUK._staff or 'куратор' in dcUK._role):
            return '""'
        if dcUK.cmd == 'setField':
            try:
                flag = None
                toWell(1, 'busy')
                i = 0
                for ch in dcUK.buf.split('¤'):
                    if ch:
                        pk, _, val = ch.partition('=')
                        dc = DC(unid=pk, dbAlias='nv_SessionSt', fullName=dcUK.fullName, _superUser=dcUK._superUser)
                        i += 1
                        if docFromDB(dc) and dc.form != 'SessionGr':  # в списке могут быть сиссии группы(commonSessGr)
                            if dc.doc[dcUK['field']] != val:
                                dc.doc[dcUK['field']] = val
                                dc.save()
                                flag = True
                toWell(0, 'busy')
                if flag:
                    sgr = well('sessionGr_Id', dc.doc.sessionGr)
                    loadWell('SessionSt', sgr.nvgroup_id)
                return HttpResponse('OK')

            except Exception as ex:
                toWell(0, 'busy')
                loadWell('SessionSt')
                err(f'getData (cmd={dcUK.cmd}):{ex}', cat=self.form)
                return HttpResponse(f'getData for {self.form}(cmd={dcUK.cmd}): {ex}', None, 200)

        # ***

        elif dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)

        # CH GROUP
        elif dcUK.cmd == 'changeStatus':
            data = swell('sessionsGr_GrId_band', dcUK.groupdId) or []
            if dcUK.status != '1':
                data = [s for s in data if s.endswith('|active')]

        elif dcUK.cmd == 'getSgr':
                if dcUK.event:
                    ls = well('sessionsGr_GrId', dcUK.group)
                    data = [f'{dc.title}|{dc.id}' for dc in ls if dc.nvEvent == dcUK.event]
                else:  # v_lk_curator2
                    data = swell('sessionsGr_GrId_band', dcUK.group) or []
        else:
            data = [f'invalid cmd: {dcUK.cmd}']

        return json.dumps(data, ensure_ascii=False)

    # *** *** ***
    setButtons = [
                _field('selectAll', 'chb', [''], chbView='nv', edit=1, className='chbVN'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Допуск+', 'cmdSet', 'allow_s', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Доп.-', 'cmdSet', 'allow_r', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Был', 'cmdSet', 'was_s', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Не был', 'cmdSet', 'was_r', name='viewbar'),
                # _div(**style(width=10), name='viewbar'),
                # _btnD('Зачёт+', 'cmdSet', 'test_s', name='viewbar'),
    ]

    def page(self, request):
        if self._userAgent == 'mobile':
            event = _field(f'event', 'lbsd', list(['Все|'] + swell('events')),
                alias=1, edit=1, xValue='Все',
                title='выберите событие',
                name=f'event',
                **style(width=230, margin='auto'),
            )
        else:
            event = _field(f'event', 'band', swell('shortEvents'), recalcText=1,
                className='radioBand',
                **style(margin='auto'),
                title='выберите событие',
                name=f'event')

        status = _div(
            **style(margin='auto',),
            children=[_field('status', 'band', ['актив', 'все'],)
        ])

        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
            event,
        ])
        self.viewbar = self.makeViewbar(leftBtn=[status], rightBtn=self.setButtons)
        self.leftList = _field('leftList', 'band', [], className='list3str')
        return self.shamrock(addUrl='&status={status}')

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []

        if dcUK.selected:
            sgrId = dcUK.selected.partition('|')[0]
        else:  # v_lk_curator2
            sgrId = dcUK.sgrId

        sessArr = well('sessionSt_sgrId', sgrId)
        if not sessArr:
            return {'mainDocs': [('1', 'Сессии для студентов не созданы (нет даты начала)'), ]}

        sgr = well('sessionGr_Id',sgrId)
        gridStr = ''
        for sst in sessArr:
            if dcUK.status == '0' and sst.status != 'active':
                continue

            prof = well('profiles', sst.pref)
            if prof.status != 'active':
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
                
            title = _div(f"{prof.full_name}\n{sgr.d2} {s}",
                s2=1, br=1, **style(letterSpacing=1, paddingLeft=2, color=color))

            pk = sst.id
            chb = _field(f'selOne_{pk}', 'chb', [''], cmd='selOne', chbView='nv', className='checkboxFV')
            btnE = _btnEdit('cmdEdit', pk)
            btnP = _btnPref('cmdPref', f'{sst.pref}|{pk}')

            div1 = _div(children=[chb, title])

            sstBtn = sstButtons(sst, sgr, curator=True)
            gridStr = gridStr or f'{"32px "*(len(sstBtn)+2)}'
            div2 = _div(**gridStyle(gridStr),
                children=[*sstBtn, btnE, btnP])

            row = _div(className='lk_row', children=[
                _div(className='lk_left', children=[div1]),
                _div(className='lk_right', children=[div2])
            ])

            mainDocs.append([pk, row, prof and prof.full_name])

        mainDocs = [[x[0], x[1]] for x in sorted(mainDocs, key=lambda x: x[2])]
        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        dcUK = r.dcUK
        self.title = dcUK.title or 'ЛК куратора'
        dcUK.doc.group = dcUK.group or dcUK.title
        dcUK.doc.grId = dcUK.unid

# *** *** ***

