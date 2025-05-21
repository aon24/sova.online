# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.common import sndErr
from arm.tools.first import err
from arm.tools.DC import well, config, DC
from arm.api.forms.formTools import style, _div, _field, _btnD, _teg, _tabNew
from arm.api.forms.classPage import Page
from arm.api.forms.YandexDisk.YandexTools import makeVideoY, getVideoUrlY, testYDFolder, getYDisk, y_makeFolder
from arm.api.forms.YandexDisk.VKTools import makeVideoVK, getVideoUrlVK
from arm.tools.httpMisc import nvResponse

import json

# *** *** ***


class SessionTmpl(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js', ]
        self.title = 'Шаблон'
        self.dbAlias = 'nv_SessionTmpl'

        super().__init__(request)

    # ***

    @sndErr
    def getData(self, dcUK):
        if dcUK.cmd == 'createYD':
            stm = well('sessionTmpl_id', dcUK.id)
            y, serviceName, hide = getYDisk()
            m = DC()
            nveText = well('eventsByCode', stm.nvEvent)
            try:
                alias = stm.title.strip()
                alias = ''.join(c for c in alias if c.isalnum() or c in ' -_.')
                if alias:
                    # y_makeFolder returned 200 (if OK) or None (if error)
                    rc = y_makeFolder(y, f'{serviceName}/{nveText}', m)  # disk:/Новый век/сессии
                    rc = rc and y_makeFolder(y, f'{hide}/{nveText}', m)  #  disk:/Новый век(hide)/сессии
                    rc = rc and y_makeFolder(y, f'{serviceName}/{nveText}/{stm.id}_{alias}', m)  # disk:/Новый век/сессии/46_<alias>
                    rc = rc and y_makeFolder(y, f'{hide}/{nveText}/{stm.id}', m)  # disk:/Новый век(hide)/сессии/46
                    return nvResponse(m.log, status=rc or 400)
                else:
                    return nvResponse('title is empty', status=400)
            except Exception as ex:
                return nvResponse(f'{ex}\n{m.log}', status=400)

        if dcUK.cmd == 'getVideoUrlY':
            return getVideoUrlY(dcUK)
        if dcUK.cmd == 'getVideoUrlVK':
            return getVideoUrlVK(dcUK)

        elif dcUK.cmd == 'makeVideoY':
            data = makeVideoY(dcUK)
        elif dcUK.cmd == 'makeVideoVK':
            data = makeVideoVK(dcUK)
        else:
            data = f'invalid cmd: {dcUK.cmd}'
            err(f'invalid cmd: {dcUK.cmd}', cat='SessionTmpl.getData')

        if data is None:
            return json.dumps(data, ensure_ascii=False)
        else:
            return f'Server error. cmd: {dcUK.cmd}'

    # ***

    def page(self, request):
        main = _div(**style(height='100%', overflow='auto'), children=[
            _div('Видеоматериалы', className='h2'),
            _teg('fieldset', className='videoMaterial', name='videoMaterial', children=[
                _teg('legend', ' Защищенное видео ', **style(margin='auto', textAlign='center')),
                # 1 - not saved
                _div(name='notSaved', **style(textAlign='center'), children=[
                    _btnD('Новый документ. Сохранить.', 'save', title='Ctrl+S', **style(maxWidth=260), className='toolbar-button'),
                ]),
                # 2 - not created
                _div(name='createYD', **style(textAlign='center'), children=[
                    _btnD('Создать папку на Yandex-диске', 'createYD', **style(maxWidth=260), className='toolbar-button'),
                ]),
                # add video
                _div(name='openYD', **style(textAlign='center'), children=[
                    _btnD('1. Загрузить на Яндекс-диск', 'openYD', className='toolbar-button'),
                    _btnD('2. Засекретить и обновить', 'makeVideoY', className='toolbar-button'),
                ]),
            ]),
            _field('videoGrid', 'grid'),

            _field('Y', 'chb', [], fd=1, **style(display='none')),
            _field('YDcreated', 'chb', [], fd=1, **style(display='none')),
            _field('openYDurl', 'fd', **style(display='none')),

        ])

        # ***

        mind = _div(**style(height='100%', display='grid', gridTemplateRows='auto 1fr'), children=[
            _div('Учебно-методические материалы', className='h2', **style(margin=5, color='#480')),
            _tabNew(xName='UM_Table_FD', tabs=[
                ('Видео', main, 70),
                ('Материалы', self.materials(tmpl=True), 100),
                ('Задания', self.jobs(tmpl=True), 80),
            ], center=True)
        ])
        if self.noicons:
            table = [
                ('1️⃣', self.common(tmpl=True), 45, 'информация'),  # 🦉📓
                ('УММ', mind, 60, 'учебные материалы')
            ]
        else:
            table = [
                ('/image/i.png', self.common(tmpl=True), 50, 'информация'),
                ('/image/s_ummv.png', mind, 50, 'учебные материалы'),
            ]

        return  self.docPage([_tabNew('SST_Table_FD', tabs=table)], focus='title')

    # ***

    def queryOpen(self, r):
        dcUK = r.dcUK
        doc = dcUK.doc
        doc.status = doc.status or 'active'
        doc.title = doc.title.strip()

        if dcUK.mode in ['new', 'edit']:
            if dcUK.mode == 'new':
                if dcUK.sourceDoc:
                    sourceDoc = well('sessionTmpl_id', dcUK.sourceDoc)
                    for k in ['nvEvent', 'sticker', 'title', 'lector', 'DESCRIPTION', 'notes']:
                        if sourceDoc[k]:
                            doc[k] = sourceDoc[k]
                else:
                    doc.nvEvent = dcUK.nvEvent
            if 'преподаватель' in dcUK._role:
                if doc.lector and dcUK.fullName not in doc.lector:
                    doc.lector += f'\n{dcUK.fullName}|{dcUK._profilePK}'
                else:
                    doc.lector = f'{dcUK.fullName}|{dcUK._profilePK}'

                for l in doc.lector.split('\n'):
                    fio = l.partition('|')[0]
                    fio = '.'.join([x[:1] for x in fio.split()]) + '.'  # A.A.A.

        doc.sticker = doc.sticker or well('stickerByCode', dcUK.nvEvent)
        if doc.sticker:
            doc.stickerImg = json.dumps([_div(**style(width=260, height=160, backgroundSize='100% 100%', backgroundImage=f"url('{doc.sticker}')"))], ensure_ascii=False)

        if config.serviceName and config.Y_OAuthToken:
            doc.y = '1'
            if dcUK.mode != 'new':
                alias = doc.title.strip()
                alias = ''.join(c for c in alias if c.isalnum() or c in ' -_.')
                if testYDFolder(doc):
                    doc.YDcreated = 1
                path = f"{config.serviceName}/{well('eventsByCode', doc.nvEvent)}/{doc.id}_{alias}"
                doc.openYDurl = f'https://disk.yandex.ru/client/disk/{path}'

        if doc.videoList and doc.videoList[0] != '[':
            doc.videoList = json.dumps([{'url': it} for it in doc.videoList.split('\n') if it], ensure_ascii=False)

    def querySave(self, dcUK):
        return True

# *** *** ***


def queryOpenForGrSt(doc, student=None):
    '''
    вызываается из queryOpen форм SessionSt, SessionGr
    заполняет поля для формы SessionSt (if student=True) or for SessionGr (if student=None)
    '''
    if student:
        docGr = well('sessionGr_Id', doc.sessionGr)
        docTm = well('sessionTmpl_id', docGr.sessionTmpl)

        doc.duration = docGr.duration
        doc.date_begin = docGr.date_begin
        doc.date_end = docGr.date_end
        doc.curator = docGr.curator
        doc.lector = docGr.lector
        doc.status = docGr.status
        # doc.semester = docGR.semester

        doc.group_fd = well('groups_groupId', docGr.nvgroup).title
        doc.nvgroup_fd = f'{doc.group_fd}|{docGr.nvgroup}'

        for i in range(1, 6):
            doc[f'job{i}'] = docGr[f'job{i}'] or docTm[f'job{i}']

        doc.title = docTm.title
    else:  # SessionGr
        docTm = well('sessionTmpl_id', doc.sessionTmpl)

        for i in range(1, 6):
            doc[f'job{i}'] = docTm[f'job{i}']

        doc.lector = doc.lector or docTm.lector
        doc.openTmpl = f"{docTm.title}|previewNew|title={docTm.title}&form=SessionTmpl&unid={docTm.id}&dbAlias=nv_SessionTmpl&rsMode=edit"

    doc.nvEvent = docTm.nvEvent
    doc.partLabel = docTm.partLabel
    doc.description = docTm.description

    if docTm.videoList and docTm.videoList != '[]':
        if docTm.videoList[0] != '[':
            doc.videoList_FD = json.dumps([{'url': it} for it in docTm.videoList.split('\n') if it], ensure_ascii=False)
        else:
            doc.videoList_FD = docTm.videoList

    doc.fm = docTm.fm
    doc.mtx = docTm.mtx
    doc.href = docTm.href
    doc.rtf = docTm.rtf
    doc.colorStyleMap = docTm.colorStyleMap


# *** *** ***

