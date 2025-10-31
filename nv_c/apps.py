from arm.settings import BASE_DIR
from django.apps import AppConfig
import os


class nv_c(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'nv_c'
    path = os.path.join(BASE_DIR, 'nv_c')

# *** *** ***
