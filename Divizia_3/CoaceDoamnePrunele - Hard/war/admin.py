from django.contrib import admin

from .models import Fight, FightEvent, Person

admin.site.register(Person)
admin.site.register(Fight)
admin.site.register(FightEvent)
