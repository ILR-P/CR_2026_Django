from django.db import models
from django.db.models import Q

MAX_HEALTH = 100


class Person(models.Model):
    class Rank(models.TextChoices):
        PRIVATE = "private", "Private"
        CORPORAL = "corporal", "Corporal"
        SERGEANT = "sergeant", "Sergeant"
        LIEUTENANT = "lieutenant", "Lieutenant"
        CAPTAIN = "captain", "Captain"
        MAJOR = "major", "Major"
        COLONEL = "colonel", "Colonel"
        GENERAL = "general", "General"

    # id comes from people.json so fight data can refer to it directly
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.PositiveSmallIntegerField()
    # set by the drafting task; blank = registered but not drafted yet
    rank = models.CharField(max_length=12, choices=Rank, blank=True, default="")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} (#{self.id})"


class Soldier(models.Model):
    """A drafted person. `health` is shared by every fight the soldier is in,
    which is exactly why it must only be changed under a row lock."""

    person = models.OneToOneField(Person, primary_key=True, on_delete=models.CASCADE, related_name="soldier")
    health = models.IntegerField(default=MAX_HEALTH)

    @property
    def id(self):
        return self.person_id

    class Meta:
        ordering = ["person_id"]
        constraints = [models.CheckConstraint(condition=Q(health__gte=0), name="soldier_health_non_negative")]

    def __str__(self):
        return f"Soldier {self.person}"


class Fight(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    # kept as class attributes so existing code can say Fight.PENDING
    PENDING, RUNNING, DONE, FAILED = Status.PENDING, Status.RUNNING, Status.DONE, Status.FAILED

    id = models.IntegerField(primary_key=True)  # external fight id
    soldier_a = models.ForeignKey(Soldier, on_delete=models.CASCADE, related_name="fights_as_a")
    soldier_b = models.ForeignKey(Soldier, on_delete=models.CASCADE, related_name="fights_as_b")
    status = models.CharField(max_length=10, choices=Status, default=Status.PENDING, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Fight {self.id}"


class FightEvent(models.Model):
    """One attack. Created when the fight data is imported (applied=False);
    flipped to applied=True in the same transaction that lowers the health,
    so a retried/duplicated task can never apply a hit twice."""

    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name="events")
    sequence = models.PositiveIntegerField()  # order inside the fight
    attacker = models.ForeignKey(Soldier, on_delete=models.CASCADE, related_name="attacks")
    defender = models.ForeignKey(Soldier, on_delete=models.CASCADE, related_name="hits_taken")
    damage = models.PositiveIntegerField()
    applied = models.BooleanField(default=False)
    defender_health_after = models.IntegerField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["fight", "sequence"]
        constraints = [models.UniqueConstraint(fields=["fight", "sequence"], name="uniq_event_per_fight_seq")]

    def __str__(self):
        return f"Fight {self.fight_id} #{self.sequence}: {self.attacker_id} -> {self.defender_id} ({self.damage})"
