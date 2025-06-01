import time
import zlib, base64, json

# *** *** ***

class DC(object):

    def __init__(self, dc=None, **kv):
        self.__dict__['_d_'] = {}
        if dc:
            if type(dc) is dict:
                self.__dict__['_f_'] = {k.upper(): str(v or '') for (k, v) in dc.items()}
            else:
                self.__dict__['_f_'] = {k: v for (k, v) in dc._f_.items()}
        else:
            self.__dict__['_f_'] = {}
        for k, v in kv.items():
            self.__dict__['_f_'][k.upper()] = str(v or '')

    def A(self, fieldName):
        s = self._f_.get(fieldName.upper())
        return s.split('\n') if s else []

    def D(self, fieldName):
        s = ''
        for k in self._f_.get(fieldName.upper(), '').split('\n'):
            if k:
                try:
                    s += time.strftime('%d.%m.%Y\n', time.strptime(k.partition(' ')[0], '%Y-%m-%d'))
                except:
                    s += k + '\n'
        return s[:-1] if s else ''

    def DT(self, fieldName):
        dt = self._f_.get(fieldName.upper(), '')
        try:
            return time.strftime('%d.%m.%Y %H:%M:%S', time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        except:
            return ''

    def loadDoc(self):
        from arm.tools.dbToolkit import DJ
        from arm.tools.dbToolkit import Book
        if self.dbAlias.startswith('nv_'):
            return DJ.docFromDB(self)
        else:
            return Book.docFromDB(self)

    def save(self):
        if not config.DEMO_MODE or self._superUser:
            from arm.tools.dbToolkit import DJ
            from arm.tools.dbToolkit import Book
            if self.dbAlias.startswith('nv_'):
                return DJ.docSaveDB(self)
            else:
                return Book.docSaveDB(self)

    def __str__(self):
        return 'DC: -----------\n' + '\n'.join(x for x in [f'{k} = {self._f_[k][:200]}' for k in sorted(self._f_)])

    def __getattr__(self, fieldName):  # dbg = dc.dateBegin
        if fieldName == 'doc':
            return self._d_
        elif fieldName == '_KV_':
            return self._f_
        return str(self._f_.get(fieldName.upper(), ''))

    def __setattr__(self, fieldName, fieldValue):
        if fieldName == 'doc':
            self.__dict__['_d_'] = fieldValue
        else:
            self._f_[fieldName.upper()] = str(fieldValue or '')

    def __getitem__(self, fieldName):  # dbg = dc['dateBegin']
        return str(self._f_.get(fieldName.upper()) or '')

    def __setitem__(self, key, value):
        self._f_[key.upper()] = str(value or '')

    def items(self):
        return self._f_.items()

    def keys(self):
        return self._f_.keys()

# *** *** ***


config = DC()  # from sova.ini: setting.py -> urls.py -> yandex-disk

# *** *** ***


class DCC(object):
    '''
    то же, что и DC, но без пребразования в строки
    может хранить объекты, числа и т.д.
    '''

    def __init__(self, dc=None, **kv):
        if dc:
            if type(dc) is dict:
                self.__dict__['_f_'] = {k.upper(): v for (k, v) in dc.items()}
            else:
                self.__dict__['_f_'] = {k.upper(): v for (k, v) in dc._f_.items()}
        else:
            self.__dict__['_f_'] = {}
        for k, v in kv.items():
            self.__dict__['_f_'][k.upper()] = v

    def __str__(self):
        return 'DC: -----------\n' + '\n'.join(x for x in [f'{k} = {self._f_[k]}' for k in sorted(self._f_)])

    def __getattr__(self, fieldName):
        return self._f_.get(fieldName.upper(), '')

    def __setattr__(self, fieldName, fieldValue):
            self._f_[fieldName.upper()] = fieldValue

    def __setitem__(self, key, value):
        self._f_[key.upper()] = value

    def __getitem__(self, key):
        return self._f_.get(key.upper())

    def items(self):
        return self._f_.items()

    def keys(self):
        return self._f_.keys()

# *** *** ***


CLS = {}  # защищенные справочники
SCLS = {}  # справочники, к которым есть дуступ через апи

# *** *** ***


class DCDump(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, DC):
            return obj.__dict__
        return super().default(obj)


def wellSize(s=None):
    import math
    l = len(json.dumps(CLS if s else SCLS, cls=DCDump))
    return f"{'CLS' if s else 'SCLS'}: {math.trunc((l+1023)/1024)}k"


def well(*keys):
    cls = CLS
    for k in keys[:-1]:
        cls = cls.get(k)
        if not cls:
            return ''

    return cls.get(keys[-1], '') if type(cls) is dict else cls


def clearWell(k):
    if well(k):
        well(k).clear()
    else:
        toWell({}, k)


def toWell(d, *keys):
    cls = CLS
    for k in keys[:-1]:
        CLS[k] = cls.get(k, {})
        cls = CLS[k]
    cls[keys[-1]] = d

# *** *** ***


def swell(*keys):
    cls = SCLS
    for k in keys[:-1]:
        cls = cls.get(k)
        if not cls:
            return ''

    return cls.get(keys[-1], '') if type(cls) is dict else cls


def clearSwell(k):
    if swell(k):
        swell(k).clear()
    else:
        toSwell({}, k)


def toSwell(d, *keys):
    cls = SCLS
    for k in keys[:-1]:
        SCLS[k] = cls.get(k, {})
        cls = SCLS[k]
    cls[keys[-1]] = d

# *** *** ***


def getRoot(dc, v):
    try:
        if v[-1] != '}':
            v = zlib.decompress(base64.b64decode(v)).decode()
        v = json.loads(v)
        for kb, vb in v.items():
            dc[kb] = vb
    except Exception as ex:
        from arm.tools.first import err
        s = f'Error in body: {ex}'
        dc.err = s
        err(s, cat='getBody')


def getBody(value):
    dc = DC()
    if not value:
        return dc

    for k, v in value.items():
        if k != 'body':
            if k.endswith('_id'):
                dc[k[:-3]] = v
            dc[k] = v
        elif v:
            getRoot(dc, v)

    return dc

