# -*- coding: utf-8 -*-
'''
Created on 24 apr 2020

@author: aon
'''

# *** *** ***
from arm.settings import API_DIR
from arm.tools.common import setVersionFiles
from arm.tools.first import err, versionString
from arm.tools.DC import DC, well, toWell
from arm.api.forms.formTools import infoPage, infoQueryOpen, _btnNew, _teg, _btnD, _fileShow, style, _div, _field, labell, labeldc, gridStyle, labField, label
from arm.api.forms.toolbars import toolbar

from django.http import HttpResponse

import json
import importlib
import uuid
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
    if (not page):
        page = {'draft': 'a_design'}.get(dcUK.dbAlias, '')

    if page:
        opg = well('forms', page)
        if opg:
            return opg

        path = f'arm.api.forms.{page}.{page}'

        try:
            module = importlib.import_module(path)
            opg = getattr(module, page)(request)
            toWell(opg, 'forms', page)
            return opg
        except Exception as ex:
            # return err(f'Page not found: "{path}"', cat='getPageObj')
            return err(f'Page not found: "{path}"\n {ex} \n*** *** *** {traceback.format_exc()}', cat='getPageObj')

# *** *** ***

class Page(object):
    '''
    urlForms - словарь в форме, хранит url для форм. КЛЮЧ: form+mode, возвращает "apigetc?loadForm&outlet.gru::2113546371"
    form-json - в глобальном словаре готовый json. КЛЮЧ: 'form::CRC-СУММА'
    '''

    def __init__(self, request):
        self.styles = ''
        self.urlForms = {}  # key = '-'.join([key, mode, multiPage, smartPhone ...etc])

        for a in ['jsCssUrl', 'jsCssUrlRead', 'jsCssUrlEdit', 'dbAlias', 'noCaching']:
            not getattr(self, a, None) and setattr(self, a, '')

        self.title = getattr(self, 'title', 'sova.online')
        self.form = getattr(self, 'form', 'noform')
        self.leftWidth = getattr(self, 'leftWidth', 0)
        self.status = well('status')

        if self.jsCssUrl:
            self.jsCssUrlRead = self.jsCssUrlEdit = setVersionFiles(self.jsCssUrl, API_DIR)
        else:
            self.jsCssUrlRead = setVersionFiles(self.jsCssUrlRead, API_DIR)
            self.jsCssUrlEdit = setVersionFiles(self.jsCssUrlEdit, API_DIR)

    # *** *** ***

    def getJsDoc(self, request):
        '''
        fормирует словарь для отправки клиенту
        '''
        dcUK = request.dcUK

        if not dcUK.doc:
            dcUK.doc = DC()
        dcUK.doc.form = dcUK.doc.form or self.form
        if dcUK.mode in ['edit', 'admin']:  # чтобы можно было установить новое значение в queryOpen
            do = {k: dcUK.doc[k] for k in dcUK.doc.keys()}  # save oldValues in 'do'

        if dcUK.dbAlias.startswith('nv_'):
            dcUK.unid = dcUK.unid or dcUK.doc.id
        elif dcUK.dbAlias != 'no':
            if dcUK.unid == 'new' or dcUK.doc.unid == 'new':
                dcUK.unid = dcUK.doc.unid = uuid.uuid4().hex
            else:
                dcUK.unid = dcUK.unid or dcUK.doc.unid or uuid.uuid4().hex

        try:
            self.queryOpen(request if self.form == 'login' else dcUK)

            fv = {}  # fieldValues- KV для отправки клиенту
            for k, v in dcUK.doc.items():  # dcUK.doc - DC-object
                if 'PASSW' not in k:
                    if type(v) == str:
                        fv[k] = v.replace('\u2028', ' ').replace('\u2029', ' ')
                    else:
                        fv[k] = v
            ds = dict(
                    form=self.form,
                    fieldValues=fv,
                    rsMode=dcUK.mode,
                    dbAlias=dcUK.dbAlias or self.dbAlias,
                    fullName=dcUK.fullName,
                    unid=dcUK.unid,
                    urlForm=self.getUrl(request),
                    cssJsUrl=self.getJsCssUrl(dcUK.mode),
                    version=f'{versionString}',
                    fd=dcUK.fd
                )
            if  dcUK.mode == 'new':
                ds['oldValues'] = {k: '' for k in fv}
            elif dcUK.mode in ['edit', 'admin']:  # чтобы можно было установить новое значение в queryOpen
                # костыль, чтобы никто не видел поля с оценкой, если есть noAss_fd
                ds['oldValues'] = {k: do.get(k, '') for k in fv if do.get(k, '') != fv[k] and not (fv.get('NOASS_FD') and k.startswith('ASSLEC'))}
        except Exception as ex:
            df = str(dcUK.doc)
            tr = str(traceback.format_exc())
            err(f'{ex}\n{dcUK._QUERY}\n{df}\n{tr}', cat='queryOpen')

            dcUK.doc['0_queryOpen_EX'] = f'{ex}'
            dcUK.doc['1_Traceback'] = f'{tr}'
            dcUK.doc['2_Fields'] = f'{df}'
            dcUK.doc['3_Query'] = dcUK._QUERY
            infoQueryOpen(dcUK)
            dcUK.key = 'Exception'
            dcUK.mode = 'read'
            ds = dict(
                fieldValues=dcUK.doc._KV_,
                rsMode=dcUK.mode,
                urlForm=self.getUrl(dcUK),
                cssJsUrl=[f'/api/jsv?forms/info/info.js'],
                version=f'{versionString}',
                fd='1',
                _view_='1'
            )

        return json.dumps(ds, ensure_ascii=False).replace('</script', '<\/script')

    def queryOpen(self, dcUK): pass

    def querySave(self, dcUK): return True

    def afterSave(self, dcUK, pk=None): return True

    def getData(self, dcUK): return  # вызывется из GET-xhr для загрузки каких-либо данных

    def putData(self, dcUK, buf): return HttpResponse(status=400)  # вызывется из PUT-xhr для загрузки каких-либо данных

    def getJsCssUrl(self, mode):
        if mode in ['read', 'preview']:
            return self.jsCssUrlRead
        else:
            return self.jsCssUrlEdit

    # *** *** ***

    def getUrl(self, request):
        '''
        возвращает url для загрузки формы формы
        сама форма хранится в глоб. словаре 'form-json', в url ключ для этого словаря
        '''
        key = '-'.join([
            request.dcUK.key,
            request.dcUK.mode,
            request.dcUK.userAgent,
            request.dcUK.userRole,
        ])

        if (not self.noCaching) and (key in self.urlForms):
            return self.urlForms[key]

        try:
            if request.dcUK.key == 'Exception':
                pg = infoPage(request)
                jsPage = json.dumps(pg, ensure_ascii=False, sort_keys=True)
                jsCss = 'Exception'
                urlForm = f'/api/get/loadForm?form=info::Exception'
                toWell(jsPage, 'form-json', 'info::Exception')
                return urlForm
            else:
                pag = self.page(request)
                jsCss = str(self.getJsCssUrl(request.dcUK.mode))  # чтобы изменение js-css сбрасывали кэш

                pg = deepcopy(pag)
                pg = self.parseCell(pg)
                jsPage = json.dumps(pg, ensure_ascii=False, sort_keys=True)
                crc = crc32((jsPage + jsCss).encode(), 0)
                if self.noCaching:
                    urlForm = f'/api/get/loadForm?form={self.form}::{crc}'
                else:
                    urlForm = f'/api/getc/loadForm?form={self.form}::{crc}'
        except Exception as ex:
            err(f'{self.form}\n{traceback.format_exc()}', cat='classPage.getUrl')
            return f'error-{self.form}-classPage.getUrl'

        self.urlForms[key] = urlForm
        toWell(jsPage, 'form-json', f'{self.form}::{crc}')

        return urlForm

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


    def navigator(self, dcVP, maxHeight=500):
        if dcVP.userAgent == 'mobile':
            width = 85
        else:
            width = 170
    
        if dcVP.fieldName:
            key = f'view={dcVP.fieldName}-{dcVP.dbAlias}-{dcVP.viewKey}'  # api/get/loadSubCats?... передается в classReview
        else:
            key = f'form={dcVP.form}'  # api/get/loadSubCats?... передается в classPage
    
    
        cat = _field('cat', 'list', list(dcVP.cats.keys()), alias=1, className='navBtn', listItemClassName='rsvTop')
    
        # при вызове doc.changeDropList('subCat') в url подставится значение поля "CAT" вместо {FIELD}
        # при вызове doc.changeDropList('subCat', 'ss') в url подставится строка "ss" вместо {FIELD}
        subCat = _field('subCat', 'list', f'CAT|||/api/get/loadSubCats?{key}&cat={{FIELD}}',
            **style(maxHeight=maxHeight, overflow='hidden auto', width='90%', margin='auto', display='block'),
            saveAlias=1, evenColor='#f4f8ff', default=-1)

        return _div(**style(paddingTop=7,verticalAlign='top', width=width, position='relative'),
            children=[
                cat,
                subCat,
        ])

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
            self.leftList['attributes']['style'] = dict(overflow='hidden auto', height='100%', width=self.leftWidth)
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

    def materials(self, tmpl=None, gr=None, st=None):
        return _div(**style(margin='0 5px', paddingTop=5, height='100%', overflow='auto',
                    display='grid', gridTemplateRows='auto 1fr'), children=[
            _div(children=[
                _fileShow('fm', label='файлы', fd=not tmpl),
                _div('По теме', className='labl'),
                labell('Текст', skip=not tmpl),
                _field('mtx', 'tx', fd=not tmpl, name='mtx'),
                labell('Ссылка', skip=not tmpl),
                _field('href', 'links', **style(width='100%'), fd=not tmpl, name='href'),
            ]),

            _div(children=[_field('rtf', 'rtf', readOnly=not tmpl, fd=not tmpl)],
                **style(position='relative', width='100%', height='calc(100% - 10px)', marginTop=5,
                    border='2px solid #888', background='#fff')
            ),
            _field('COLORSTYLEMAP', 'fd', skip=tmpl, **style(display='none'))
        ])

    def common(self, tmpl=None, gr=None, st=None):
        '''
        readOnly настроен на name='student':
        readOnly: {student: doc => doc.fieldValues['STUDENT_FD']}
        '''
        return _div(**style(margin='0 5px', paddingTop=5, height='100%', overflow='auto'), children=[

            _field('nvEvent', 'lbsd', '/api/well?clues=events', alias=1, fd=not tmpl,
                **style(color='#048', fontWeight=700, margin='0 auto 10px', width=230, textAlign='center')
            ),

            _field('openTmpl', 'btn', fd=1, skip=not gr, className='toolbar-button', **style(display='block', margin='auto', width='90%')),

            label('Заголовок', skip=not tmpl),
            _field('title', 'tx', name='title', className='h2', skip=not tmpl, **style(background='#fff', border='1px solid #0000ff80')),
            _field('title', 'tx', className='h2', skip=not st, fd=1),

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
            _field('duration', 'lbse', '/api/well?clues=duration', **style(width=110, margin='auto', paddingTop=5),
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
            _div(**style(margin=5, border='1px solid #048')),
            labell('Комментарий', name='adminOnly'),
            _field('notes', 'tx', **style(margin='0 5px', display='block'), name='adminOnly'),
            label('Статус', **style(margin='5px 0', display='inline-block')),
            _field('status', 'lbsd', self.status, name='student', placeholder='выбирай', alias=1, **style(margin=5, display='inline-block'))
        ])

    btnSaveClose = _div(**style(textAlign='center',paddingTop=4),children=[toolbar.saveClose,toolbar.close_])

    def docPage(self, fields, tool=None, focus='no', **kv):
        return _div(className='bg52', focus=focus, **kv,
            children=[
                _div(className='toolbar', children=tool or [toolbar.saveClose, toolbar.close_]),
                _div(className='page', children=fields),
            ])
