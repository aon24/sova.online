# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''
from arm.tools.common import sndErr
from arm.tools.first import err
from arm.tools.DC import well, config, DC
from arm.api.forms.formTools import style, _div, _tab, _field, _btnD, _teg, gridStyle
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

        if data != None:
            return json.dumps(data, ensure_ascii=False)
        else:
            return f'Server error. cmd: {dcUK.cmd}'

    # ***

    def page(self, request):
        main = _div(**style(height='100%', overflow='auto'), children=[
            # _div(**gridStyle('auto auto'), children=[
            #     _div('Видеоматериалы', className='h2'),
            #     _field('restrict', 'band', ['сессии', 'лекции|1', 'только сотрудники|2']),
            # ]),
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
                #
                # _div(name='openVK', **style(textAlign='center'), children=[
                #     _field('openVK', 'btn', fd=1, className='toolbar-button', **style()),
                #     _btnD('2. Обновить', 'makeVideoVK', className='toolbar-button'),
                # ]),
                #
                # _div(name='openDisk', **style(textAlign='center'), children=[
                #     _field('openDisk', 'btn', fd=1, className='toolbar-button', **style()),
                #     _btnD('2. Обновить', 'makeVideoDisk', className='toolbar-button'),
                # ]),
            ]),
            _field('videoGrid', 'grid'),

            _field('Y', 'chb', [], fd=1, **style(display='none')),
            _field('YDcreated', 'chb', [], fd=1, **style(display='none')),
            _field('openYDurl', 'fd', **style(display='none')),

        ])

        # ***

        table = [
            ('1️⃣', self.common(tmpl=True), 50),  # 🦉📓
            ('Видео', main, 80),
            ('Материалы', self.materials(tmpl=True), 90),
        ]

        # vkAut = _btnD('vkAut', 'vkAut', '/api/runCmd?cmd=openPage&file=vk_auth.html', title='', className='toolbar-button')

        # tool = [toolbar.saveClose, toolbar.close_]
        return  self.docPage([_tab(width=110, tabs=table, ah=6)], focus='title')  # , tool=tool)

    # ***

    def queryOpen(self, dcUK):
        doc = dcUK.doc
        doc.status = doc.status or 'active'
        doc.title = doc.title.strip()

        if dcUK.mode == 'new':
            if dcUK.sourceDoc:
                sourceDoc = well('sessionTmpl_id', dcUK.sourceDoc)
                for k in ['nvEvent', 'sticker', 'title', 'lector', 'DESCRIPTION', 'notes']:
                    if sourceDoc[k]:
                        doc[k] = sourceDoc[k]
            else:
                doc.nvEvent = dcUK.nvEvent
                doc.sticker = f'/static/pictures/Программа/owl-{dcUK.nvEvent}.jpg'

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

        # if config.vk_group_id:
        #     url = f'https://vk.com/video/playlist/-{config.vk_group_id}_{doc.vk_album_id}'
        #     doc.openVK = f'1. Загрузить в плейлист VK|openVK|{url}'
        #
        # nveText = well('eventsByCode', doc.nvEvent)
        # doc.openDisk = f'1. Загрузить на сервер|openDisk|/api/openDisk?{nveText}/{doc.alias}'

        # print(type(doc.videoList), doc.videoList)
        if doc.videoList and doc.videoList[0] != '[':
            doc.videoList = json.dumps([{'url': it} for it in doc.videoList.split('\n') if it], ensure_ascii=False)

    def querySave(self, dcUK):
        return True
