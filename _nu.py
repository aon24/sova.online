# -*- coding: utf-8 -*-
'''
Created on 9 apr. 2017

@author: aon
'''

import arm.tools.first as log

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn, TCPServer
from socket import getfqdn
import urllib.parse
import sys
import platform
import threading

# *** *** ***

_blocking_errnos = { 9, 11 }

# *** *** ***

wsgiApplication = None
versionStr = f'HTTP {log.versionString}({sys.platform}) {platform.system()}/{platform.release()}'

# *** *** ***

class SovaHttpServer(ThreadingMixIn, HTTPServer):

    def __init__(self, addr, handler):
        HTTPServer.__init__(self, addr, handler)

    def server_activate(self):
        self.socket.settimeout(30)  # таймаут ответа клиента
        self.socket.listen(256)  # по умолчанию 5, в торнадо 128

        _blocking_errnos.add(10053)  # блокировка ошибки разрыва соединения

    def server_bind(self):
        """Override server_bind to store the server name."""
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        try:
            self.server_name = getfqdn(host)
        except:
            self.server_name = 'local'
        self.server_port = port                      

# *** *** ***

class wsgiRH(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, frmat, *args):
        log.dbg('addr %r, %s' % (self.client_address, frmat % args), cat='http-server')

    def log_error(self, frmat, *args):
        log.err('addr %r, %s' % (self.client_address, frmat % args), cat='error-http-server')

    def version_string(self):
        return versionStr

    def get_environ(self):
        env = dict(
            SERVER_SOFTWARE='WsgiSovaServer/1.0',
            SERVER_PROTOCOL=self.request_version,
            REQUEST_METHOD=self.command,
            REMOTE_ADDR=self.client_address[0],
            CONTENT_TYPE=self.headers.get('content-type', self.headers.get_content_type()),
            )
        env['wsgi.input'] = self.rfile
        env['wsgi.version'] = (1, 0)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = True
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        path, _, query = self.path.partition('?')

        env['PATH_INFO'] = urllib.parse.unquote(path, 'iso-8859-1')
        env['QUERY_STRING'] = query

        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host

        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for k, v in self.headers.items():
            k = k.replace('-', '_').upper()
            v = v.strip()
            if k not in env:
                if 'HTTP_' + k in env:
                    env['HTTP_' + k] += ',' + v
                else:
                    env['HTTP_' + k] = v

        return env

    # *** *** ***

    def handle_one_request(self):
        if 1:#try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return

            result_iter = wsgiApplication(self.get_environ(), self.start_response)  # run WSGI-application
            if result_iter:
                for data in result_iter:
                    if data:
                        self.wfile.write(data)
                        self.wfile.flush()

#        except Exception as ex:
#            self.log_error('svServer.py.handle_one_request: %r', ex)
#            self.close_connection = True

    # *** *** ***

    def start_response(self, status, response_headers):
        try:
            st = int(status.partition(' ')[0])
            self.send_response(st)

            for rh in response_headers:
                self.send_header(*rh)

            self.end_headers()

        except Exception as ex:
            self.log_error(f'svServer.py.start_response: {ex}')
            self.close_connection = True

# *** *** ***

if __name__ == '__main__':
    import os
    from pathlib import Path

    baseDir = Path(__file__).resolve().parent
    if sys.platform == 'win32':
        sys.path.insert(0, str(baseDir / 'libForUSB'))
    else:
        venvLib = baseDir / 'venv' / 'lib'
        try:
            py = [f for f in os.listdir(venvLib) if f.lower().startswith('python3')][0]
            venv = venvLib / py / 'site-packages'
            sys.path.insert(0, str(venv))
        except:
            pass

    import arm.wsgi
    wsgiApplication = arm.wsgi.application

    port = 8081

    server = SovaHttpServer(('', port), wsgiRH)
    threading.Thread(target=server.serve_forever).start()
    log.snd(f'''
=== === === HTTP WSGI server started (port {port})
=== === === {versionStr}
=== === === Application: "DJANGO.application"
=== === === logLevel: INFO''', cat='Start')

# *** *** ***

