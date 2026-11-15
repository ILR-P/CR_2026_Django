from django.core.validators import MinValueValidator
from django.db import models

TYPES = [('human', 'Human'), ('elf', 'Elf'), ('orc', 'Orc'), ('troll', 'Troll')]
TEAMS = {'human': 'A', 'elf': 'A', 'orc': 'B', 'troll': 'B'}


class Fighter(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPES)
    health = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    max_health = models.PositiveIntegerField(default=0)
    attack_points = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def team(self):
        return TEAMS[self.type]

    def __str__(self):
        return self.name


class Fight(models.Model):
    first = models.ForeignKey(Fighter, on_delete=models.CASCADE, related_name='fights_first')
    second = models.ForeignKey(Fighter, on_delete=models.CASCADE, related_name='fights_second')
    winner = models.ForeignKey(Fighter, null=True, on_delete=models.CASCADE, related_name='wins')


class Step(models.Model):
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name='steps')
    attacker = models.ForeignKey(Fighter, on_delete=models.CASCADE, related_name='+')
    defender = models.ForeignKey(Fighter, on_delete=models.CASCADE, related_name='+')
    damage = models.PositiveIntegerField()
    attacker_health = models.PositiveIntegerField()
    defender_health = models.PositiveIntegerField()

    class Meta:
        ordering = ('id',)