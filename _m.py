#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == '__main__':
    baseDir = Path(__file__).resolve().parent
    venvLib = baseDir / 'venv' / 'lib'
    try:
        py = [f for f in os.listdir(venvLib) if f.lower().startswith('python3')][0]
        venv = venvLib / py / 'site-packages'
        sys.path.insert(0, str(venv))
    except:
        pass

    from django.core.management import execute_from_command_line
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arm.settings')
    execute_from_command_line(sys.argv)
