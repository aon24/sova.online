'''
Created on 24 apr 2020

@author: aon
'''

# *** *** ***
from arm.settings import BASE_DIR, DEBUG
from arm.tools.common import setVersionFiles
from arm.tools.first import err, versionString
from arm.tools.DC import DC, well, toWell, swell
from arm.api.forms.formTools import infoPage, infoQueryOpen, _btnNew, _teg, _btnD, _fileShow, style, _div, _field, labell, labeldc, gridStyle, labField, label
from arm.api.forms.toolbars import toolbar

from django.http import HttpResponse

import os
import json
import importlib
from copy import deepcopy
from zlib import crc32
import traceback

# *** *** ***

def getPageObj(request):
    '''
    у документа из БД форма, у страницы page
    '''
    dcUK = request.dcUK

    page = dcUK.form or (dcUK.doc and dcUK.doc.form) or dcUK.page

    if page:
        key = f"{page}-{dcUK.mode or 'read'}-{dcUK._userAgent}-{dcUK._role}-{dcUK._staff}-{dcUK.noicons}"
        opg = well('forms', key)
        if opg:
            return opg

        path = f'arm.api.forms.{page}.{page}'

        try:
            module = importlib.import_module(path)
            opg = getattr(module, page)(request)

            toWell(opg, 'forms', key)
            return opg
        except Exception as ex:
            if DEBUG:
                err(f'Page not found: "{path}"\n {ex} \n*** *** *** {traceback.format_exc()}', cat='getPageObj')
            else:
                err(f'Page not found: "{path}"', cat='getPageObj')

# *** *** ***

class Page(object):
    '''
    urlForms - словарь в форме, хранит url для форм. КЛЮЧ: form+mode+.., возвращает "api/getc?loadForm&outlet.gru::2113546371"
    form-json - в глобальном словаре готовый json. КЛЮЧ: 'form::CRC-СУММА'
    '''
    styles = '<link href="/static/fonts/home.css" rel="stylesheet">\n'

    def __init__(self, request):
        dcUK = request.dcUK
        self.urlForms = ''
        self.mode = dcUK.mode
        self._userAgent = dcUK._userAgent
        self._role = dcUK._role
        self._staff = dcUK._staff
        self.noicons = dcUK.noicons

        for a in ['_VIEW_', '_PAGE_', 'jsCssUrl', 'jsCssUrlRead', 'jsCssUrlEdit', 'dbAlias', 'noCaching', 'styles']:
            not getattr(self, a, None) and setattr(self, a, '')

        self.title = getattr(self, 'title', 'sova.online')
        self.form = getattr(self, 'form', 'noform')
        self.leftWidth = getattr(self, 'leftWidth', 0)
        self.status = swell('status')

        API_DIR = os.path.join(BASE_DIR, 'arm', 'api')
        if self.jsCssUrl:
            self.jsCssUrlRead = self.jsCssUrlEdit = setVersionFiles(self.jsCssUrl, API_DIR)
        else:
            self.jsCssUrlRead = setVersionFiles(self.jsCssUrlRead, API_DIR)
            self.jsCssUrlEdit = setVersionFiles(self.jsCssUrlEdit, API_DIR)

    # *** *** ***

    def getJsDoc(self, request, coocieBtn=None):
        '''
        fормирует словарь для отправки клиенту
        '''
        dcUK = request.dcUK
        if dcUK.doc:  # доступ к конкретному документу
            if dcUK.dbAlias.startswith('nv_') and dcUK.unid:  # django
                if dcUK.dbAlias.rpartition('_')[2] != self.form and self.form not in ['info', 'html']:
                    return '{}'  # защита от подмены form=qqq в url "/api/opendoc?dbAlias=nv_SessionSt&unid=5481&form=SessionGr&mode=edit"

            dcUK.doc.form = dcUK.doc.form or self.form
            if dcUK.mode == 'edit':  # чтобы можно было установить новое значение в queryOpen
                do = {k: dcUK.doc[k] for k in dcUK.doc.keys()}  # save oldValues in 'do'

        else:
            do = {}
            dcUK.doc = DC(form=self.form)

        try:
            self.queryOpen(request)

            fv = {}  # fieldValues- KV для отправки клиенту
            for k, v in dcUK.doc.items():  # dcUK.doc - DC-object
                if 'PASSW' not in k:
                    fv[k] = v.replace('\u2028', ' ').replace('\u2029', ' ')

            ds = dict(
                    form=self.form,
                    fieldValues=fv,
                    rsMode=self.mode,
                    dbAlias=dcUK.dbAlias or self.dbAlias,
                    fullName=dcUK.fullName,
                    unid=dcUK.unid,
                    urlForm=self.getUrl(request),
                    cssJsUrl=self.getJsCssUrl(request),
                    version=f'{versionString}',
                    fd=dcUK.fd
                )
            if self._VIEW_:  # виды (не документы) - игнорировать сохранение
                ds['_VIEW_'] = 1
            if self._PAGE_:  # страница (не документ) - игнорировать ESC
                ds['_PAGE_'] = 1
            if coocieBtn:  # наш сайт использует файлы cookie
                ds['coocieButton'] = 1

            if self.mode == 'new':
                ds['oldValues'] = {k: '' for k in fv}
            elif self.mode == 'edit':  # чтобы можно было установить новое значение в queryOpen
                if self.form == 'info' and not request.dcUK._superUser:
                    ds['oldValues'] = {}
                else:
                    ds['oldValues'] = self.getOldValue(request, fv, do)
        except Exception as e:
            ex = str(e)
            tr = str(traceback.format_exc())
            url = f'{dcUK._path}?{dcUK._QUERY}'
            err(f'{ex}\nURL: {url}\n{tr}', cat='queryOpen')
            if ex == 'Access denied':
                dcUK.doc = DC()
            else:
                dcUK.doc['3_Fields'] = str(dcUK.doc)

            dcUK.doc['0_Exception'] = ex
            dcUK.doc['1_Traceback'] = tr
            dcUK.doc['2_URL'] = url
            infoQueryOpen(request)
            dcUK.key = 'Exception'

            ds = dict(
                fieldValues=dcUK.doc._KV_,
                rsMode='read',
                urlForm=self.getUrl(request),
                cssJsUrl=[f'/api/jsv?forms/info/info.js'],
                version=f'{versionString}',
                fd='1',
                _view_='1'
            )
        return json.dumps(ds, ensure_ascii=False)

    def getOldValue(self, request, fv, do):
        '''do - old(fields from DB), fv - after queryOpen'''
        return {k: do.get(k, '') for k in fv if do.get(k, '') != fv[k]}

    def page(self, request=None): pass

    def queryOpen(self, request): pass

    def querySave(self, dcUK): return True

    def afterSave(self, dcUK, pk=None): return True

    def getData(self, dcUK): return  # вызывется из GET-xhr для загрузки каких-либо данных

    def putData(self, dcUK, buf): return HttpResponse(status=400)  # вызывется из PUT-xhr для загрузки каких-либо данных

    def getJsCssUrl(self, request):
        if request.dcUK.mode in ['read', 'preview']:
            return self.jsCssUrlRead
        else:
            return self.jsCssUrlEdit

    # *** *** ***

    def getUrl(self, request):
        '''
        возвращает url для загрузки формы
        сама форма хранится в глоб. словаре 'form-json', в url ключ для этого словаря
        '''
        if request.dcUK.key == 'Exception':
            if not well('form-json', 'info::Exception'):
                pg = infoPage('read')
                jsPage = json.dumps(pg, ensure_ascii=False, sort_keys=True)
                toWell(jsPage, 'form-json', 'info::Exception')
            return '/api/get/loadForm?form=info::Exception'

        if self.urlForms and not self.noCaching:
            return self.urlForms

        try:
            pag = self.page(request)
            jsCss = str(self.getJsCssUrl(request))  # чтобы изменение js-css сбрасывали кэш

            pg = deepcopy(pag)
            pg = self.parseCell(pg)
            jsPage = json.dumps(pg, ensure_ascii=False, sort_keys=True)
            crc = crc32((jsPage + jsCss).encode(), 0)
            if self.noCaching:  # кэширование естанавливается на кленте на 30 дней
                self.urlForm = f'/api/get/loadForm?form={self.form}::{crc}'
            else:
                self.urlForm = f'/api/getc/loadForm?form={self.form}::{crc}'
            toWell(jsPage, 'form-json', f'{self.form}::{crc}')
            return self.urlForm
        except:
            err(f'{self.form}\n{traceback.format_exc()}', cat='classPage.getUrl')
            return f'error-{self.form}-classPage.getUrl'

    # *** *** ***

    def parseCell(self, cell):
        if type(cell) is str:
            return cell
        if not (type(cell) is dict and not cell.get('skip')):
            return None

        row = cell.get('children')
        if 'fieldProps' in cell and not cell['fieldProps']:
            del cell['fieldProps']
        if row:
            ls = []
            for it in row:
                c = self.parseCell(it)
                c and ls.append(c)
            cell['children'] = ls

        return cell

    # *** *** ***

    def shamrock(self, *, addUrl='', refs=1, expand=None, previewUrl=None, focus='upList'):
        if not self.form:
            raise Exception('self.form')
        sh = self.sham(addUrl=addUrl, refs=refs, expand=expand, previewUrl=previewUrl)

        return _div(focus=focus, className='bg51',
                    **style(overflow='hidden', position='absolute', inset=0),
                    children=[
                        _div(focus=focus,
                            **style(height='100%', background='linear-gradient(0deg, #ffFFff30, #f4fffaff)', overflow='hidden', maxWidth=1200, margin='auto'),
                            children=[sh])
                ])
            
    def sham(self, *, addUrl='', refs=1, expand=None, previewUrl=None):
        # 2 внизу экрана список тем
        previewUrl = previewUrl or f'dbAlias={self.dbAlias}'
        ls = '{leftList}' if self.leftList else '{upList}'  # js разберется
        url = f'/api/getData?form={self.form}&cmd=getSelected&selected={ls}' + addUrl
        mainList = getattr(self, 'mainList', None) or _field('mainList', 'view', expand=expand, refs=refs, limit=100000, url=url, previewUrl=previewUrl)

        if self.leftList:
            self.leftList['attributes'] = self.leftList.get('attributes', {})
            self.leftList['attributes']['style'] = dict(overflow='hidden auto', height='100%',
                background='#fff', width=self.leftWidth,)
            self.leftList['attributes']['name'] = 'shamrock1'
            if 'field' in self.leftList:
                self.leftList['fieldProps'] = self.leftList.get('fieldProps', {})
                self.leftList['attributes']['className'] = self.leftList['attributes'].get('className', 'list1str')
                self.leftList['fieldProps']['rowLength'] = 1
                self.leftList['fieldProps']['recalcText'] = self.leftList['fieldProps'].get('recalcText', 1)
            colGrid = 'auto 1fr'
        else:
            colGrid = '1fr'

        return _div(className=f"{'shamrock' if self.upField else 'shamrock2'}", children=[  # grid-template-rows: auto auto 1fr;
                self.upField,  # 1.1 вверху экрана toolbar+upFiled
                self.viewbar,  # 1.2 вверху viewbar
                _div(**style(overflow='hidden'), children=[  # 2.внизу
                    _div(**gridStyle(colGrid, height='100%'), children=[
                        self.leftList,  # 2.1 слева экрана список групп для курса
                        _div(children=[mainList], id='mainList',  # 2.2 справа экрана список тем
                            ** style(height='100%', overflow='hidden auto'),
                        ),
                    ]),
                ]),
            ])

    # *** *** ***

    def makeViewbar(self, leftBtn=None, rightBtn=None, name=None, expand=None, style=None):
        if expand and rightBtn:
            rightBtn.append(_field('expand', 'chb', ['▼', '►'],
                title='сложить/показать', char=1, name=expand,
                style=dict(fontSize=24, width=10, position='absolute', top=0, right=10)))
        
        if style:
            style['height'] = 40
        else:
            style = dict(height=40)
        return _div(name=name,
                className='viewbar',
                style=style,
                children=[
                    _div(children=(leftBtn or [])),
                    _div(children=(rightBtn or [])),
                ]
            )
    
    # *** *** ***

    # ***

    def materials(self, tmpl=None):
        return _div(**style(margin='0 5px', paddingTop=5, height='100%', overflow='auto',
                    display='grid', gridTemplateRows='auto 1fr'), children=[
            _div(children=[
                labell('Краткое описание (если поле пустое, материал скрыт)', skip=not tmpl, name='mtxLabel'),
                _field('mtx', 'tx', fd=not tmpl, name='mtx', **style(margin=10, fontSize=20, textAlign='center')),
                _fileShow('fm', label='файлы', fd=not tmpl),
                labell('Ссылки', name='href'),
                _field('href', 'links', **style(width='100%'), fd=not tmpl, name='href'),
            ]),

            _div(name='rtf', children=[_field('rtf', 'rtf', readOnly=not tmpl, fd=not tmpl)],
                **style(position='relative', width='100%', height='calc(100% - 10px)', marginTop=5,
                    border='2px solid #888', background='#fff')
            ),
            _field('COLORSTYLEMAP', 'fd', skip=tmpl, **style(display='none'))  # fd - not save!
        ])

    def jobs(self, tmpl=None, gr=None, st=None):
        jobs = []
        for i in range(1, 6):
            jobs.append(
                _div(name=f'job{i}', children=[
                    labell(f'Задание {i}'),
                    _field(f'job{i}', 'tx', name='student', fd=st),
                    _teg('fieldset', skip=not st, **style(background='#ffc'), children=[
                        _teg('legend', f' Результат {i} ', **style(margin='auto', textAlign='center')),

                        _fileShow(f'fo{i}', label='файлы'),
                        labell('Текст'),
                        _field(f'txo{i}', 'tx'),
                        labell('Ссылка'),
                        _field(f'hrefo{i}', 'links', **style(width='100%')),
                    ]),
                    labell(f'Оценка', skip=not st),
                    _field(f'estimate{i}', 'tx', skip=not st, name='student'),
                    _div(**style(margin=10, height=2, background='#036')),
                ])
            )
        return _div(**style(margin='0 5px', paddingTop=5, height='100%', overflow='auto',),
                    children=jobs)

    def common(self, tmpl=None, gr=None, st=None):
        '''
        readOnly настроен на name='student':
        readOnly: {student: doc => doc.fieldValues['STUDENT_FD']}
        '''
        return _div(**style(margin='0 5px', paddingTop=5, height='100%', overflow='auto'), children=[

            _field('nvEvent', 'lbsd', '/api/well?clues=events', alias=1, fd=not tmpl,
                **style(color='#03', fontWeight=700, margin='0 auto 10px', width=230, textAlign='center')
            ),

            _field('openTmpl', 'btn', fd=1, skip=not gr, className='toolbar-button', **style(display='block', margin='auto', width='90%')),

            label('Заголовок', skip=not tmpl),
            _field('title', 'tx', name='title', className='h2', skip=not tmpl, **style(background='#fff', border='1px solid #0000ff80')),
            _field('title', 'tx', className='h2', skip=not st, fd=1, **style(textAlign='center')),

            _field('fullName', 'fd', className='h3', skip=not st),

            _div(**style(padding='2px 0', margin='10px auto', width=280, display='grid', gridTemplateColumns='95px 90px 95px'), children=[
                _field('group_fd', 'fd', className='label labelc'),
                _btnD('подменить', 'changeGroup', **style(height=20), name='chGr'),
                _btnD('удалить', 'delGroup', **style(height=20), name='delGr'),
                _field('other_group_fd', 'fd', className='label labelc'),
            ], skip=not st, name='owner'),

            _div(**gridStyle('95px 90px 95px', padding='2px 0', margin='10px auto', width=280), children=[
                _field('other_fd', 'fd', fd=1, className='label labelc'),
                labeldc('подмена из', **style(height=20), name='chGr'),
                _field('owner_fd', 'fd', fd=1, className='label labelc'),
            ], skip=not st, name='other'),

            _teg('fieldset', className='btnGroup',
                skip=not st, name='student',
                children=[
                    _div(
                        **gridStyle('auto  auto'), children=[
                            _div(children=[_field('allow_s', 'chb', ['Допуск'], className='label')]),
                            _div(children=[_field('test_s', 'chb', ['Зачет'], className='label')]),
                    ]),
                    _div(
                        **gridStyle('120px 120px 40px', marginTop=8, paddingTop=5,
                            border='0 solid #aaa', borderTopWidth=1),
                        children=[
                            _div(children=[_field('pay_s', 'chb', ['Оплата'], className='label')]),
                            _div(children=[_btnD('платежи', 'payList')]),
                            _div(name='adminOnly', children=[ _btnNew(cmd='newPay', style=dict(height=32, left=235, top=1))]),

                    ]),
            ]),

            # _field('semester', 'lbsd', '/api/well?clues=semester', alias=1, fd=st, skip=tmpl, name='semester',
            #     **style(margin='5px auto 10px', width=310, textAlign='left')
            # ),

            _div(**gridStyle('1fr 10px 1fr', width=260, margin='5px auto'), children=[
                    labeldc('Начало'), _div(), labeldc('Окончание'),
                    _field('date_begin', 'dt'), _div(), _field('date_end', 'dt'),
                ],
                fd=st,
                skip=tmpl  # убрать в шаблоне, только чтение у студента
            ),
            _field('duration', 'lbse', '/api/well?clues=duration', **style(width=130, margin='auto', paddingTop=5),
                placeholder='время',fd=st,skip=tmpl),  # убрать в шаблоне, только чтение у студента

            _div(children=[
                    label('Куратор', skip=tmpl),
                    _field('curator', 'lbsd', '/api/well?clues=куратор2', **style(marginLeft=5) , common='clsCurator', skip=tmpl),
                    label('Преподаватель'),
                    _field('lector', 'lbmd', '/api/well?clues=преподаватель2', **style(marginLeft=5), common='clsLector'),
                ],
                fd=st,
                **style(margin='5px 0', padding=0),
            ),

            _btnD('Выберите картинку для эскиза', 'openImg', skip=not tmpl, className='fileLabel'),
            _field('sticker', **style(marginLeft=5), skip=not tmpl, placeholder='Введите ссылку (url) '),
            _field('stickerImg', 'json', fd=1, name='stickerImg', skip=not tmpl),

            *labField('Описание', 'description', 'tx', **style(marginLeft=5), fd=not tmpl),

            self.noteStatus(st),

            # _div(children=[self.btnSaveClose], skip=st),
            # _div(children=[self.btnSaveClose], name='adminOnly', skip=not st),
        ])

    def noteStatus(self, st=None):
        return _div(**style(textAlign='right', skip=st), children=[
            _div(**style(margin=5, border='1px solid #036')),
            labell('Комментарий', name='adminOnly'),
            _field('notes', 'tx', **style(margin='0 5px', display='block'), name='adminOnly'),
            label('Статус', **style(margin='5px 0', display='inline-block')),
            _field('status', 'lbsd', self.status, name='student', placeholder='выбирай', alias=1, **style(margin=5, display='inline-block'))
        ])

    def docPage(self, fields, tool=None, focus='no', **kv):
        if not tool:
            if self.mode in ['new', 'edit']:
                tool = [toolbar.saveClose, toolbar.close_]
            else:
                tool = [toolbar.close_]
        return _div(className='bg52', focus=focus, **kv,
            children=[
                _div(className='toolbar', children=tool),
                _div(className='page', children=fields),
            ])
