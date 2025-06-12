'''
Created on 2024

@author: aon24
'''

from arm.settings import MEDIA_ROOT
from arm.tools.DC import DC, well, config
from arm.tools.first import snd, err
from arm.tools.common import sndErr

import yadisk
from yadisk.exceptions import PathNotFoundError, ForbiddenError

import os

# *** *** ***

@sndErr
def getVideoUrlY(dcUK):
    y, _, hide = getYDisk()

    stmplId = None
    # //у сессии студня есть sgr_id, у сессии группы есть tmpl_id, у шаблона есть id. Питон разберется
    # let sessId = this.doc.fieldValues['SESSIONGR_ID'] || this.doc.fieldValues['SESSIONTMPL_ID'] || this.doc.fieldValues['ID'];
    if dcUK.fromForm == 'SessionSt':
        sgr = well('sessionGr_Id', dcUK.id)
        if not sgr:
            err(f'session_Gr not found. idSt="{dcUK.id}"', cat='Y-error')
            return f'File "{dcUK.file}" not found'
        stmplId = sgr.SESSIONTMPL_ID

    stm = well('sessionTmpl_id', stmplId or dcUK.id)
    if not stm:
        err(f'session_Tmpl not found. idTmpl="{stmplId or dcUK.id}"', cat='Y-error')
        return f'File "{dcUK.file}" not found'

    nveText = well('eventsByCode', stm.nvEvent)
    pathDest = f'{hide}/{nveText}/{stm.id}'

    try:
        for f in y.listdir(pathDest):
            if f['name'] == dcUK.file:
                return f['file']
    except Exception as ex:
        err(f'Exception: {ex} idGr="{dcUK.idGr}" PATH="{pathDest}" dcUK.file="{dcUK.file}"', cat='Y-error')
        return f'File "{dcUK.file}" not found'

    err(f'getVideoUrl not found. idGr="{dcUK.idGr}" PATH="{pathDest}/{dcUK.file}"', cat='Y-error')
    return f'File "{dcUK.file}" not found'

# *** *** ***


@sndErr
def makeVideoY(dcUK):
    y, serviceName, hide = getYDisk()

    stm = well('sessionTmpl_id', dcUK.id)
    nveText = well('eventsByCode', stm.nvEvent)

    alias = stm.title.strip()
    alias = ''.join(c for c in alias if c.isalnum() or c in ' -_.')
    pathSour = f'{serviceName}/{nveText}/{stm.id}_{alias}'
    pathDest = f'{hide}/{nveText}/{stm.id}'

    try:
        for item in y.listdir(pathSour):
            if item['type'] == 'file':
                y.move(f'{pathSour}/{item["name"]}', f'{pathDest}/{item["name"]}', overwrite=True)
    except Exception as ex:
        err(f'listdir({pathSour}): \n{ex}', cat='makeVideoY')

    dirInfo = []
    for item in y.listdir(pathDest):
        it = {}
        it['platform'] = 'yandex-disk'
        it['url'] = item['name']
        it['name'] = stm.title
        it['image'] = stm.sticker or '/image/yandexDisk.png'
        dirInfo.append(it)

    return dirInfo

# ***

@sndErr
def createStructure(m, server=None):
    m.log = ''
    if server:
        y, serviceName, hide = None, config.serviceName, None
    else:
        y, serviceName, hide = getYDisk()

    y_makeFolder(y, serviceName, m)
    y and y_makeFolder(y, hide, m)

    for k, arr in well('sessionTmpl_nve').items():
        if k != 'all':
            nveText = well('eventsByCode', k)
            y_makeFolder(y, f'{serviceName}/{nveText}', m)  # disk:/Новый век/сессии
            y and y_makeFolder(y, f'{hide}/{nveText}', m)  #  disk:/Новый век(hide)/сессии

            for stm in arr:
                alias = stm.alias.strip()
                alias = ''.join(c for c in alias if c.isalnum() or c in ' -_.')
                if alias:
                    y_makeFolder(y, f'{serviceName}/{nveText}/{stm.id}_{alias}', m)  # disk:/Новый век/сессии/46 <alias>
                    y and y_makeFolder(y, f'{hide}/{nveText}/{stm.id}', m)  # disk:/Новый век(hide)/сессии/46
                else:
                    s = f'--- {stm.title} не имеет алиаса для Y-disk\n'
                    m.log += s
                    snd(s, cat='Y-make-folder')

# *** *** ***

def getYDisk():
    token, serviceName = config.Y_OAuthToken, config.serviceName
    if  token and serviceName:
        return (yadisk.YaDisk(token=token), serviceName, f'{serviceName}(hide)')
    else:
        return None, None, None

# *** *** ***

@sndErr
def testYDFolder(doc):
    y, serviceName, hide = getYDisk()
    nveText = well('eventsByCode', doc.nvEvent)
    alias = doc.title.strip()
    alias = ''.join(c for c in alias if c.isalnum() or c in ' -_.')
    path = f'{serviceName}/{nveText}/{doc.id}_{alias}'
    try:
        rc = y.get_type(f'{serviceName}/{nveText}/{doc.id}_{alias}')
        if rc == 'dir':
            rc = y.get_type(f'{hide}/{nveText}/{doc.id}')
            return rc == 'dir'
    except Exception as ex:
        return err(f'path="{path}" {ex}', cat='testYDFolder') or ''

# *** *** ***


@sndErr
def y_makeFolder(y, path, m):

    def _err(s):
        m.log += f'{s}\n'
        err(s, cat=cat)
        raise Exception(s)

    def _snd(s):
        m.log += f'{s}\n'
        snd(s, cat=cat)

    # ***

    if y:
        cat = 'Y-make-folder'
        try:
            typ = y.get_type(path)
            if typ != 'dir':
                return _err(f'Нельзя создать папку "{path}".\nЕсть файл с таким именем')
            else:
                _snd(f'Папка "{path}" уже существует')
                return 200

        except ForbiddenError:
            return _err(f'Нельзя создать папку "{path}".\nОшибка доступа')

        except PathNotFoundError:
            try:
                y.mkdir(path)
                _snd(f'Создана папка "{path}"')
                return 200
            except Exception as ex:
                return _err(f'{ex}')

        except Exception as ex:
            return _err(f'{ex}')

    else:
        cat = 'Server-make-folder'
        p = os.path.join(MEDIA_ROOT, path)

        try:
            os.makedirs(p, exist_ok=True)
            _snd(f'Создана папка "{path}"')
            return 200

        except Exception as ex:
            return _err(f'Нельзя создать папку "{path}".\n{ex}')
    
    # ***
