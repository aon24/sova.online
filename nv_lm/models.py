'''
Created on 2024

@author: aon24
'''
from arm.tools.loadWell import loadWell
from nv.models import PageManager, _body, _status

from django.db import models

# *** *** ***

class Module(models.Model):
    docs = PageManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        loadWell('Module')

    starting_time = models.CharField(max_length=20, null=True)
    end_time = models.CharField(max_length=20, null=True)
    status = _status()
    body = _body()

# *** *** ***

