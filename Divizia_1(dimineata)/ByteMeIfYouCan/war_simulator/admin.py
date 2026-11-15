from django.contrib import admin
from .models import Unit, Fight, FightStep


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit_type', 'team', 'health', 'attack_points')
    list_filter = ('team', 'unit_type')
    search_fields = ('name',)


class FightStepInline(admin.TabularInline):
    model = FightStep
    extra = 0
    readonly_fields = ('step_number', 'attacker', 'defender', 'damage', 'attacker_health_after', 'defender_health_after')


@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):
    list_display = ('id', 'fighter_1', 'fighter_2', 'winner', 'created_at')
    list_filter = ('winner__team', 'created_at')
    inlines = [FightStepInline]


@admin.register(FightStep)
class FightStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'fight', 'step_number', 'attacker', 'defender', 'damage')
