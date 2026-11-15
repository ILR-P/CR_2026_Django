from django.contrib import admin

from .models import Fight, FightEvent, Person, Soldier

for m in (Person, Soldier, Fight, FightEvent):
    admin.site.register(m)
