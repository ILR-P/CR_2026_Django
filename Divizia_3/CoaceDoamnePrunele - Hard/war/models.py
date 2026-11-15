from django.conf import settings
from django.db import models


class Person(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    age = models.PositiveSmallIntegerField()
    key = models.CharField(max_length=200, blank=True, default='')

    rank = models.CharField(max_length=32, blank=True, default='')
    health = models.PositiveSmallIntegerField(default=settings.MAX_HEALTH)

    class Meta:
        ordering = ['external_id']
        verbose_name_plural = 'people'

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    @property
    def health_pct(self):
        return round(100 * self.health / settings.MAX_HEALTH)


class Fight(models.Model):
    external_id = models.IntegerField(unique=True) 
    blue = models.ForeignKey(
        Person, to_field='external_id', related_name='blue_fights',
        on_delete=models.CASCADE,
    )
    red = models.ForeignKey(
        Person, to_field='external_id', related_name='red_fights',
        on_delete=models.CASCADE,
    )
    winner = models.ForeignKey(
        Person, to_field='external_id', related_name='wins',
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    simulated = models.BooleanField(default=False)

    class Meta:
        ordering = ['external_id']

    def __str__(self):
        return f'Fight #{self.external_id}'


class FightEvent(models.Model):

    fight = models.ForeignKey(Fight, related_name='events', on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    attacker = models.ForeignKey(
        Person, to_field='external_id', related_name='attacks',
        on_delete=models.CASCADE,
    )
    defender = models.ForeignKey(
        Person, to_field='external_id', related_name='hits_taken',
        on_delete=models.CASCADE,
    )
    damage = models.PositiveIntegerField()
    defender_health_after = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['fight_id', 'sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['fight', 'sequence'], name='uniq_event_per_fight'
            )
        ]

    def __str__(self):
        return f'{self.attacker_id} -> {self.defender_id} ({self.damage})'
