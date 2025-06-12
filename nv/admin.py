from nv import models as mmm
from nv_c import models as mmm_c
from nv_lm import models as mmm_lm
from nv_reports import models as mmm_reports
from arm.tools.first import err

from django.db.models import Model
from django.db.models.base import ModelBase

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Отключаем автоматическую регистрацию User
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')  # Добавьте нужные поля

# *** *** ***

admin.site.site_title = 'Админ'
admin.site.site_header = 'Администратор'
admin.site.index_title = 'Новый век'


all_ml = {}
model_names = []
model_fields = {}


def makeModel(appModels):
    # вызывается для каждого приложения
    for e in dir(appModels):
        model = getattr(appModels, e)
        if isinstance(model, ModelBase) and issubclass(model, Model):
            all_ml[e.lower()] = model
            model_names.append(e.lower())
            fi = [f.name for f in model._meta.fields]
            fi_id = [f'{f}_id' for f in fi]
            model_fields[e] = [fi, fi_id]


makeModel(mmm)
makeModel(mmm_c)
makeModel(mmm_lm)
makeModel(mmm_reports)


def getModel(dcUK, cat):
    db, _, model = dcUK.dbAlias.rpartition('_')
    if not db.startswith('nv'):
        err(f'"{dcUK.dbAlias}" invalid db', cat=cat)
        return None, None

    m = all_ml.get(model.lower())
    if not m:
        err(f'"{dcUK.dbAlias}" not in all_models', cat=cat)
        return None, None

    return m, model

