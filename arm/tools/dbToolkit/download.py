# -*- coding: utf-8 -*-

from arm.tools.first import err
from arm.tools.httpMisc import nvResponse
from arm.settings import DB_DIR

import zlib
import os

# *** *** ***


def downloadFile(request):

    def _err(s):
        err(s, cat='error-download.py')
        return nvResponse(s, None, 400)

    dcUK = request.dcUK
    # if notReader(dcUK.dbAlias, dcUK.fullName):
    #     return _err(f'uploadFile: Access denied for user {dcUK.fullName}')

    try:
        fullname = os.path.join(DB_DIR, 'files', dcUK.path)
        with open(fullname, 'rb') as f:
            buf = f.read()

        if not buf:
            return _err('Zero-length file')

        if dcUK.zip == 'Z':
            buf = zlib.decompress(buf)

        if 'charset' not in dcUK.type and dcUK.utf:
            dcUK.type += '; charset=UTF-8'

        return nvResponse(buf, dcUK.type or 'Application/attachment', 200)

    except Exception as ex:
        return _err(f'Exception (q={dcUK.query}): {ex}')

# *** *** ***
