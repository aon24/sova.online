'''
Created on 2024

@author: aon24
'''

from arm.settings import BASE_DIR
from django.apps import AppConfig
import os


class nv_lm(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'nv_lm'
    path = os.path.join(BASE_DIR, 'nv_lm')

# *** *** ***
