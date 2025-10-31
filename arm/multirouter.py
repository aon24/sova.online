# -*- coding: utf-8 -*- 
'''
Created 2020

@author: aon

для миграции раскомментировать TEMPLATES в файле setting.py


************* File __arm_init.sh **************
#!/usr/bin/env bash
rm -r -f ./nv/migrations
rm -r -f ./DB/common.sqlite3
rm -r -f ./DB/nv.sqlite3
python _m.py makemigrations
python _m.py makemigrations nv
python _m.py migrate --database=default
python _m.py migrate --database=nv
python _m.py createsuperuser
python _m.py createsuperuser

************* File __nv.sh ************** (./nv/migrations exist)
#!/usr/bin/env bash
rm -r -f ./DB/nv.sqlite3
python _m.py migrate --database=nv

'''
# *** *** ***


class MultiRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'nv':
            return 'nv'
        elif model._meta.app_label == 'nv_lm':
            return 'lm'
        elif model._meta.app_label == 'nv_reports':
            return 'reports'
        else:
            return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'nv':
            return 'nv'
        elif model._meta.app_label == 'nv_lm':
            return 'lm'
        elif model._meta.app_label == 'nv_reports':
            return 'reports'
        else:
            return None

    def allow_relation(self, obj1, obj2, **hints):
        return True  # Return True if a relation between obj1 and obj2 should be allowed

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None  # None if the router has no opinion.

# *** *** ***
