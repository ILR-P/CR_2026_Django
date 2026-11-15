from django.db import models


class Person(models.Model):
    # The id comes from the server's /people list (0..99), so we keep it.
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    # Filled in by the drafting task. Empty (null) = not drafted yet.
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
