'''
Created on 14 февр. 2025 г.

@author: aon24
'''
from arm.settings import BASE_DIR
from arm.tools.DC import DC
from arm.tools.first import snd, err

from pathlib import Path
from datetime import datetime
import subprocess
import os


def main(m):
    cat = 'nv_lm/agents/db/DB_backup.py'
    try:
        day_name = datetime.now().strftime('%A')  # Полное название
        # Пути к папкам
        folder_a = Path(BASE_DIR, 'DB')
        folder_b = Path(BASE_DIR, m.param)
        archive_name = f'{day_name}.tar.gz'  # Имя архива

        # Создаем список всех файлов .sqlite3 в папке А
        sqlite_files = [os.path.join(folder_a, f) for f in os.listdir(folder_a) if f.endswith('.sqlite3')]  # or f.endswith('.rsf')]

        # Команда для создания архива
        command = ["tar", "-czf", os.path.join(folder_b, archive_name), "-C", folder_a] + [os.path.basename(f) for f in sqlite_files]

        # Выполняем команду
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Проверяем результат
        if result.returncode == 0:
            s = f"Архив успешно создан: {os.path.join(folder_b, archive_name)}"
            m.log=s
            snd(s,cat=cat)
        else:
            s = f"Ошибка при создании архива: {result.stderr.decode('utf-8')}"
            m.log=s
            err(s, cat=cat)
    except Exception as ex:
        m.log = ex
        err(ex, cat=cat)


if __name__ == '__main__':
    m = DC(param='DB_backup')
    main(m)
