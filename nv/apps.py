from arm.settings import BASE_DIR
from django.apps import AppConfig
import os

class nv(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'nv'
    path = os.path.join(BASE_DIR, 'nv')

# *** *** ***

