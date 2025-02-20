from arm.tools.loadWell import loadWell
from arm.tools.DC import getBody, well

from django.db import models
from django.contrib.auth.models import User

from nv.models import PageManager, txf, _body, _status

# *** *** ***

class Profile(models.Model):
    docs = PageManager()  # Менеджер status != 'deleted'
    objects = models.Manager()  # Менеджер по умолчанию

    class Meta:
        verbose_name = 'Профайл'
        indexes = models.Index(fields=['status']),

    def save(self, *args, **kwargs):
        dc = getBody({'body': self.body, 'status': self.status})
        old = well('profiles', str(self.id))
        if not old or any(dc[k] != old[k] for k in ['student_groups', 'role', 'status']):
            noSgr = None
        else:
            noSgr = 'noSgr'

        super().save(*args, **kwargs)
        loadWell('Profile', noSgr)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    programm = models.TextField(blank=True, default='nv')  # чтобы куратор видел только своих
    full_name = txf('Пользователь')

    status = _status()
    body = _body()

    def __str__(self) -> str:
        return str(self.full_name)

# *** *** ***

