# -*- coding: utf-8 -*-
import os, time, sys
from datetime import datetime

from arm.settings import LOG_DIR, DEBUG

# *** *** ***

versionString = f'Sova.online/1.0 Python/{sys.version.split()[0]}'

# *** *** ***


class SvLogger(object):
    TIME_LOOP = 60 * 60 * 6  # проверять переполнение журналов каждые 6 часов
    maxLogFiles = 10  # количество журналов
    maxLogSize = 512 * 1024  # макс. размер
    datefmt = '%d.%m.%Y %H:%M:%S'

    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)

        self.fileHandler = None
        self.logPath = os.path.join(LOG_DIR, 'sova_%d.log')
        self.logFileName = None
        self.startTime = 0

    def changeLogFile(self):
        if self.logFileName:
            try:
                if os.stat(self.logFileName).st_size < self.maxLogSize:
                    return
            except:
                pass

        self.fileHandler and self.fileHandler.close()
        logFileMode = 'a'
        ls = {}

        for i in range(self.maxLogFiles):
            try:
                ls[i] = {'time': os.stat(self.logPath % i).st_mtime, 'size': os.stat(self.logPath % i).st_size}
            except:
                ls[i] = {'time': 0}

        i = sorted(ls.keys(), key=lambda x: ls[x]['time'], reverse=True)[0]  # номер последнего журнала
        if ls[i]['time'] == 0:  # список журналов пуст
            i = 0
        elif ls[i]['size'] > self.maxLogSize:  # размер файла больше допустимого
                logFileMode = 'w'
                i += 1
                if i >= self.maxLogFiles:
                    i = 0
        self.logFileName = self.logPath % i
        self.fileHandler = open(self.logFileName, mode=logFileMode, encoding='utf-8', errors='ignore')

# *** *** ***

    def msgForLog(self, msg, cat, level):
        if time.time() - self.startTime > self.TIME_LOOP:
            self.startTime = time.time()
            try:
                self.changeLogFile()
            except Exception as ex:
                self.TIME_LOOP = 300
                print(f'{datetime.now().strftime(SvLogger.datefmt)} ERROR [LOGGING-ERROR] cat: {cat}\n{ex}\n')
                return

        s = f'{datetime.now().strftime(SvLogger.datefmt)} {level} [{cat}] {msg}\n'
        if DEBUG or level == 'ERROR':
            print(s)

        try:
            sovaLogger.fileHandler.write(s + '¤')
            sovaLogger.fileHandler.flush()
        except Exception as ex:
            ss = f'{s}\n{datetime.now().strftime(SvLogger.datefmt)} ERROR [LOGGING-ERROR] cat: {cat}\n{ex}\n'
            print(ss)


def snd(*msg, cat='snd'):
    s = ', '.join(str(x) for x in msg)
    sovaLogger.msgForLog(s, cat, 'INFO')


def dbg(*msg, cat='all'):
    if DEBUG:
        s = ', '.join(str(x) for x in msg)
        sovaLogger.msgForLog(s, cat, 'DEBUG')


def err(*msg, cat='all'):
    s = ', '.join(str(x) for x in msg)
    sovaLogger.msgForLog(s, cat, 'ERROR')

# *** *** ***


sovaLogger = SvLogger()

