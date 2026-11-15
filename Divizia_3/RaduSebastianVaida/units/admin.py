
from django.contrib import admin
from .models import Unit, Fight, FightTurn


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "type",
        "team",
        "health",
        "attack_points"
    )

    list_filter = (
        "type",
        "team"
    )

    search_fields = (
        "name",
    )

    ordering = (
        "id",
    )


class FightTurnInline(admin.TabularInline):
    model = FightTurn
    extra = 0
    readonly_fields = (
        "attacker",
        "defender",
        "attack_points",
        "attacker_health",
        "defender_health",
        "turn_number"
    )


@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "unit1",
        "unit2",
        "winner",
        "created_at"
    )

    list_filter = (
        "created_at",
    )

    inlines = [
        FightTurnInline
    ]


@admin.register(FightTurn)
class FightTurnAdmin(admin.ModelAdmin):

    list_display = (
        "fight",
        "turn_number",
        "attacker",
        "defender",
        "attack_points",
        "attacker_health",
        "defender_health"
    )

    ordering = (
        "fight",
        "turn_number"
    )
