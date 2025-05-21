# -*- coding: utf-8 -*-
"""
AON 2023

"""

from arm.tools.first import err, snd
from arm.tools.DC import DC

from django.http import HttpResponse

import traceback, time
from urllib.parse import unquote

from user_agents import parse
import gzip
import email.utils

# *** *** ***


def nvResponse(body, content_type='text/html; charset=UTF-8', status=200, request=None):
    headers = [('Content-Type', content_type), ('X-Frame-Options', 'SAMEORIGIN')]

    if type(body) is str:
        try:
            body = body.encode()
        except:
            return HttpResponse(b'nvResponsee: encode-error', content_type=None, status=500)

    if len(body) > 100 and any(c in content_type for c in ['/json', '/html', '/javascript', '/css']):
        body = gzip.compress(body)
        headers.append(('Content-Encoding', 'gzip'))

    if request and request.dcUK._path in ['image', 'jsv']:
        days = 30
        maxAge = 60 * 60 * 24 * days
        headers.append(('Expires', email.utils.formatdate(time.time() + maxAge, usegmt=True)))
        headers.append(('Cache-Control', f'max-age={maxAge}'))

    headers.append(('Content-Type', content_type))
    headers.append(('Content-Length', str(len(body))))

    # if environ.get('HTTP_RANGE') and status == 200:
    #     status = 206
    #     header.append(('Content-Range', f'bytes 0-{lbody-1}/{lbody}'))
    #

    return HttpResponse(body, status=status, headers=headers)


def badReq(par, fullName='-?-'):
    err('param: %s' % par, cat='badReq')
    return accessDenied(fullName)


def notFound(s, un=''):
    err(f'404 (fullName={un})\n{s}', cat='page not found')
    return nvResponse(f'''<h3>API-404<br/>{s}</h3> not found (un={un or '-?-'})''')


def jsonNotFound(request):
    dcUK = request.dcUK
    err(f'404. fullName={dcUK.fullName} path?query={dcUK.path}?{dcUK.query}', cat='json-object not found')
    return nvResponse(f'''404 "{dcUK.path or 'block not found'} ({dcUK.fullName or '-?-'})"''', 'application/json', 200)


def accessDenied(fullName):
    snd(fullName, cat='accessDenied')
    return nvResponse(f'Access denied for {fullName}', status=403)

# *** *** ***


def stackEx():
    return traceback.format_exc()

# *** *** ***


def httpError(ret=None):
    """
    Декоратор, пищуий в журнал ошибки.
    """

    def _wrapper1(func):

        def _wrapper2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                err(str(ex), cat=func.__name__)
                err(stackEx())
                if ret:
                    return ret, 'text/html; charset=UTF-8', f'{func.__name__},\n{ex}'

        return _wrapper2

    return _wrapper1

# *** *** ***
