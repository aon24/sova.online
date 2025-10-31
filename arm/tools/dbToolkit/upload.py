# -*- coding: utf-8 -*-

from arm.tools.common import now, today
from arm.tools.first import snd, err
from arm.tools.httpMisc import nvResponse
from arm.tools.DC import well
from arm.tools.imgHeader import what
from arm.settings import DB_DIR, BASE_DIR, DEMO_MODE

import zlib
import uuid
import os

_noCompress = 'compressed|.jpg|.jpeg|.gif|.pdf|.png|.arj|octet-stream|.zip|.rar|.7z|.dll|.exe|.avi|.mkv|.mp3|.mp4'.split('|')

# *** *** ***


def uploadFile(request):

    def _err(s):
        err(f'{s}(UN:{request.dcUK.fullName})', cat='error-upload.py')
        return nvResponse(s, status=400)

    if DEMO_MODE and not request.dcUK._superUser:
        return _err(f'uploadFile: read only for {request.dcUK.fullName}', cat='upload.py')

    defaultStore = os.path.join(DB_DIR, 'files')

    try:
        if not hasattr(request, '_files'):
            return _err('no _files')

        fi = request._files.get('bgFile')  # background image
        if fi:
            try:
                fil = os.path.join(BASE_DIR, 'static', 'pictures', request.dcUK.path, fi.name)
                with open(fil, 'bw') as fo:
                    fo.write(fi.read())

                if what(fil):
                    snd(fil, cat='upload.py (bgFile)')
                    return nvResponse('OK')
                else:
                    os.remove(fil)
                    return _err(f'{fi.name} not image (bgFile)')

            except Exception as ex:
                return _err(f'Exception: {ex}')

        fi = request._files.get('nvFile')  # filine field
        if not fi:
            return _err('unknown _files')

        buf = fi.read()
        if any(c in fi.name for c in _noCompress) or not (100 < fi.size < 10000000):
            fzip = ''
        else:
            buf = zlib.compress(buf)
            fzip = '&zip=Z'

        date_db = now('-')
        store = well('store')
        fileName = uuid.uuid4().hex.upper()
        localPath = os.path.join(today('-'), request.dcUK.dbAlias)
        s = f'path={os.path.join(localPath, fileName)}&date_db={date_db}{fzip}'
        if store:
            s += f'&store={store}'
        else:
            store = defaultStore

        fullPath = os.path.join(store, localPath)
        os.makedirs(fullPath, exist_ok=True)

        with open(os.path.join(fullPath, fileName), 'bw') as f:
            f.write(buf)
        snd(f'{s}(UN:{request.dcUK.fullName})', cat='upload')
        return nvResponse(s)

    except Exception as ex:
        return _err(f'Exception: {ex}')

# *** *** ***
