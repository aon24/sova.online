'''
Created on 2020.

@author: aon
'''
from arm.api.forms.formTools import gridStyle, style, _div, _field
from arm.api.forms.classPage import Page
from arm.tools.first import sovaLogger, err

import re, os, json

# *** *** ***

s_subCats = {}
s_DBC = {}
s_cats = ['__Все__', 'Ошибки', 'Сообщения', 'Отладка']
logList = []


class ilog(Page):
    title = 'Log'
    noCaching = True
    _PAGE_ = 1
    _VIEW_ = 1

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']

        super().__init__(request)

    def page(self, request):
        leftList = _div(**style(height='100vh', background='#44880030'),
            children=[
            _field('cat', 'list', s_cats, alias=1, className='navBtn', listItemClassName='rsvTop'),
            _field('subCat', 'list', f'CAT|||/api/get/getData?cmd=getSubCats&form=ilog&mode=new&cat={{FIELD}}',
                **style(overflow='hidden auto', width='90%', margin='auto', height='calc(100vh - 185px'),
                saveAlias=1, evenColor='#f4f8ff', default=-1)
        ])

        btns = [_div(f'{i+1}' , title='Системный журнал') for i in range(len(logList))]

        return _div(children=[
            _div(**style(overflow='hidden'), children=[
                _div(**gridStyle('170px auto', height='100%'), children=[
                    leftList,

                    _div(children=[
                        _div(**style(padding=3, background='#dfe', border='0 solid #eee', borderBottomWidth=2),
                            children=[_field('log_0_6', 'band', btns, className='logband')]
                        ),
                        _div(**style(height='calc(100vh - 50px)', maxWidth='calc(100vw - 170px)', overflow='auto', background='#fff'),
                            children=[_field('msg', 'fd', br=1, **style(font='normal 14px Courier'))]
                        )
                    ]),
                ]),
            ]),
        ])


    # *** *** ***

    def queryOpen(self, r):
        global s_subCats, logList
        r.dcUK.doc.msg = 'загрузка...'

        logList = []
        for i in range(10):
            try:
                f = sovaLogger.logPath % i
                logList.append({'time': os.stat(f).st_mtime, 'file': f})
            except:
                pass

        logList.sort(key=lambda x: x['time'], reverse=True)

        try:
            self.loadLog(0)
        except Exception as ex:
            err(f'queryOpen: {ex}', cat='classPage: log')
            s_subCats = {k:[] for k in s_cats}

    # *** *** ***

    def loadLog(self, num):
        global s_DBC, s_subCats, logList
        ALL = '__Все__'
        s_DBC = {}
        s_subCats = {k:[] for k in s_cats}

        with open(logList[int(num or 0)]['file'], 'rt', encoding='utf-8', errors='ignore') as f:
            lsMsg = f.read().split('¤')

        reCat = re.compile(r' \[(.+?)\] ')

        for msg in lsMsg:
            if ' DEBUG [' in msg:
                cat = 'Отладка'
            elif ' ERROR [' in msg:
                cat = 'Ошибки'
            else:
                cat = 'Сообщения'

            m = re.search(reCat, msg)
            if m:
                subCat = m.group(1)
            elif msg.strip():
                subCat = '_no cat_'
            else:
                continue

            if subCat not in s_subCats[ALL]:
                s_subCats[ALL].append(subCat)
            if subCat not in s_subCats[cat]:
                s_subCats[cat].append(subCat)

            for k in [f'{ALL}|', f'{ALL}|{subCat}', f'{cat}|', f'{cat}|{subCat}']:
                s_DBC[k] = s_DBC.get(k, [])
                s_DBC[k].append(msg)

        for k in s_subCats:
            s_subCats[k].sort(key=lambda k: k.lower())

    # *** *** ***

    def getData(self, dcUK):
        try:
            if dcUK.log:
                self.loadLog(dcUK.log)

            if dcUK.cmd == 'getSubCats':
                return json.dumps(s_subCats.get(dcUK.cat, []), ensure_ascii=False)
            else:
                return ''.join(reversed(s_DBC.get(dcUK.key, []))) or 'empty'
        except Exception as ex:
            err(f'{ex}', cat='form-ilog-getData ')

# *** *** ***
