# -*- coding: utf-8 -*-
'''
Created on 2020.

@author: aon
'''
from arm.tools.first import err
from arm.tools.DC import well, swell, DC, toWell
from arm.tools.loadWell import loadWell
from arm.api.forms.formTools import style, _div, _btnD, _field, _btnEdit, _btnPref
from arm.api.forms.classPage import Page
from arm.tools.dbToolkit.DJ import docFromDB
from arm.api.forms.toolbars import toolbar
from arm.api.forms.lk_tools import sstButtons

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
    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/v_lk_curator/v_lk_curator.js']
        self.leftWidth = 105
        self.dbAlias = 'nv_SessionSt'
        super().__init__(request)

    def putData(self, dcUK, buf):
        if dcUK.cmd != 'setField' or not buf:
            err(f'Unknown cmd: {dcUK.cmd}', cat=self.form)
            return HttpResponse(f'PutData for {self.form}. Unknown cmd: {dcUK.cmd}', None, 200)

        # import time
        # time.sleep(1)
        try:
            ls = buf.split('¤')
            l = len(ls) - 1
            toWell(1, 'busy')
            for i, ch in enumerate(ls):
                if ch:
                    pk, _, val = ch.partition('=')
                    dc = DC(unid=pk, dbAlias='nv_SessionSt')
                    if docFromDB(dc) and dc.form != 'SessionGr':  # в списке могут быть сиссии группы(commonSessGr)
                        if dc.doc[dcUK['field']] != val:
                            dc.doc[dcUK['field']] = val
                            dc.save()
                    if i >= l:
                        toWell(0, 'busy')
                        sgr = well('sessionGr_Id', dc.doc.sessionGr)
                        loadWell('SessionSt', sgr.nvgroup_id)
            return HttpResponse('OK')

        except Exception as ex:
            toWell(0,'busy')
            loadWell('SessionSt')
            err(f'PutData (cmd={dcUK.cmd}):{ex}', cat=self.form)
            return HttpResponse(f'PutData for {self.form}(cmd={dcUK.cmd}): {ex}', None, 200)

    # *** *** ***

    def getData(self, dcUK):
        if dcUK.cmd == 'getSelected':
            data = self.getView(dcUK)

        # CH GROUP
        elif dcUK.cmd == 'changeStatus':
            data = swell('sessionsGr_GrId_band', dcUK.groupdId) or []
            if dcUK.status != '1':
                data = [s for s in data if s.endswith('|active')]
        else:
            data = [f'invalid cmd: {dcUK.cmd}']

        return json.dumps(data, ensure_ascii=False)

    # *** *** ***
    setButtons = [
                _field('selectAll', 'chb', [''], nv=1, edit=1, className='chbVN'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Допуск+', 'cmdSet', 'allow_s', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Допуск-', 'cmdSet', 'allow_r', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Video+', 'cmdSet', 'video_s', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Video-', 'cmdSet', 'video_r', name='viewbar'),
                _div(**style(width=10), name='viewbar'),
                _btnD('Зачёт+', 'cmdSet', 'test_s', name='viewbar'),
    ]

    def page(self, request):
        self.upField = _div(children=[
            _div(className='toolbar', children=[toolbar.close_]),
            _field('status', 'band', ['актив', 'архив', 'все'], recalcText=1, **style(margin='auto', display='table', width='auto'))
        ])
        self.viewbar = self.makeViewbar(rightBtn=self.setButtons)
        self.leftList = _field('leftList', 'band', [], className='list3str')
        return self.shamrock(addUrl='&status={status}')

    # *** *** ***

    def getView(self, dcUK):
        mainDocs = []
        topStatus = dcUK.status

        if dcUK.selected:
            sgrId = dcUK.selected.split('|')[1]
        else:  # v_lk_curator2
            sgrId = dcUK.sgrId

        sessArr = well('sessionSt_sgrId', sgrId)

        if not sessArr:
            return {'mainDocs': [('1', 'Сессии для студентов не созданы (нет даты начала)'), ]}

        sgr = well('sessionGr_Id',sgrId)

        for sst in sessArr:
            if topStatus != 'все':
                if topStatus == 'актив' and sst.status != 'active':
                    continue
                if topStatus == 'архив' and sst.status != 'closed':
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

            pk = sst.pk
            chb = _field(f'selOne_{pk}', 'chb', [''], cmd='selOne', nv=1, className='checkboxFV')
            btnE = _btnEdit('cmdEdit', pk)
            btnP = _btnPref('cmdPref', f'{sst.pref}|{pk}')

            row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='32px 1fr auto auto auto auto auto auto'),
                children=[chb, title, *sstButtons(sst, sgr), btnE, btnP])

            mainDocs.append([pk, row, prof and prof.full_name])

        mainDocs = [[x[0], x[1]] for x in sorted(mainDocs, key=lambda x: x[2])]
        return {'mainDocs': mainDocs, 'refsDocs': None}

    def queryOpen(self, r):
        dcUK = r.dcUK
        self.title = dcUK.title or 'ЛК куратора'
        dcUK.doc.group = dcUK.group or dcUK.title
        dcUK.doc.grId = dcUK.unid
        dcUK.doc._view_ = 1

# *** *** ***

