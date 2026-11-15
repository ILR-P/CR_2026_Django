from django.db import models


class Person(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField(null=True, blank=True)
    health = models.IntegerField(default=100)
    extra = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class Fight(models.Model):
    PENDING, QUEUED, RUNNING, DONE, FAILED = "PENDING", "QUEUED", "RUNNING", "DONE", "FAILED"

    external_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    soldier_a = models.ForeignKey(Person, related_name="+", on_delete=models.PROTECT)
    soldier_b = models.ForeignKey(Person, related_name="+", on_delete=models.PROTECT)
    status = models.CharField(max_length=10, default=PENDING)
    winner = models.ForeignKey(Person, null=True, blank=True, related_name="+",
                               on_delete=models.SET_NULL)


class FightEvent(models.Model):
    fight = models.ForeignKey(Fight, related_name="events", on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    attacker = models.ForeignKey(Person, related_name="+", on_delete=models.PROTECT)
    defender = models.ForeignKey(Person, related_name="+", on_delete=models.PROTECT)
    damage = models.IntegerField()
    defender_health_after = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(fields=["fight", "sequence"], name="uniq_event_per_fight")
        ]