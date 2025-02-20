from arm.tools.loadWell import loadWell
from arm.tools.DC import getBody

from django.db import models

# *** *** ***


class PageManager(models.Manager):

    def get_queryset(self):
        return super(PageManager, self).get_queryset().exclude(status='deleted')

# *** *** ***


def txf(tx=None, **kv): return models.TextField(tx, blank=True, *kv)


def _body(): return txf()

def _status(): return txf('Состояние')


# *** *** ***


class Classifier(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('Classifier')

    status = _status()
    body = _body()

# *** *** ***


class SessionTmpl(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    class Meta:
        verbose_name = 'Шаблон сессии'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('SessionTmpl')

    status = _status()
    body = _body()

# *** *** ***


class NVGroup(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('NVGroup')

    status = _status()
    body = _body()

# *** *** ***


class SessionGr(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    class Meta:
        verbose_name = 'Сессия'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('SessionGr')

    nvgroup = models.ForeignKey(NVGroup, null=False, on_delete=models.CASCADE)
    sessiontmpl = models.ForeignKey(SessionTmpl, null=False, on_delete=models.CASCADE)

    date_begin = models.DateField('Дата начала', blank=True, null=True)
    status = _status()
    body = _body()

# *** *** ***


class SessionSt(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    class Meta:
        verbose_name = 'Студент'
        indexes = models.Index(fields=['sessiongr']),

    def save(self, *args, **kwargs):
        if "_MODIFIER" in self.body:

            old_sst = SessionSt.objects.values().filter(pk=self.pk)[0]
            dcOld = getBody(old_sst)
            dcNew = getBody({'body': self.body})

            super().save(*args, **kwargs)

            if dcNew.owner != dcOld.owner or self.other_group != dcOld.other_group:
                loadWell('SessionSt')

        else:  # new sst - создаются только при сохранении SessionGr или Profile
            super().save(*args, **kwargs)

    sessiongr = models.ForeignKey(SessionGr, null=False, on_delete=models.CASCADE)
    other_group = txf('Другая группа')
    pref = models.CharField(max_length=10, blank=True)

    status = _status()
    body = _body()

# *** *** ***


class Payment(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    class Meta:
        verbose_name = 'Платеж'
        indexes = models.Index(fields=['pref']),

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('Payment')

    pref = models.CharField(max_length=10, null=True)
    status = _status()
    body = _body()

# *** *** ***


from django.contrib import admin
from django.contrib.sessions.models import Session
admin.site.register(SessionTmpl)
admin.site.register(Session)

