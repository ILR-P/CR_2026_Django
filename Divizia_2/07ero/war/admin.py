from django.contrib import admin

from .models import Fight, FightStep, Unit

admin.site.register(Unit)
admin.site.register(Fight)
admin.site.register(FightStep)
