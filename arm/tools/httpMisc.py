# -*- coding: utf-8 -*-
"""
AON 2023

"""

from arm.tools.first import err

from django.http import HttpResponse

import traceback
import time
import gzip
import email.utils

# *** *** ***


def nvResponse(body, content_type='text/html; charset=UTF-8', status=200, request=None):
    headers = [('Content-Type', content_type), ('X-Frame-Options', 'SAMEORIGIN')]

    if type(body) is str:
        try:
            body = body.encode()
        except Exception:
            return HttpResponse(b'nvResponsee: encode-error', content_type=None, status=500)

    if len(body) > 100 and any(c in content_type for c in ['/json', '/html', '/javascript', '/css']):
        body = gzip.compress(body)
        headers.append(('Content-Encoding', 'gzip'))

    if request and request.dcUK._path in ['image', 'jsv', 'xImage']:
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


def notFound(request, content_type='text/html; charset=UTF-8'):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')
    err(f'{request.dcUK.fullName}({request.user.username} {ip}) {request.path}?{request.dcUK.query}', cat='Яя-api  404')
    return HttpResponse('""', content_type=content_type, status=404)


def accessDenied(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')
    err(f'{request.method}: {request.dcUK.fullName}({request.user.username} {ip}) {request.path}?{request.dcUK.query}', cat='accessDenied')
    return HttpResponse(' ', status=403)

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
