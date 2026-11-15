from django.contrib import admin

from .models import Fight, FightStep, Unit

for m in (Unit, Fight, FightStep):
    admin.site.register(m)
