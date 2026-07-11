from django.contrib import admin
from . import models as m
from django.contrib.auth.models import Permission
# Register your models here.

admin.site.register(m.User)
admin.site.register(m.Profile)
admin.site.register(m.Connection)

admin.site.register(Permission)