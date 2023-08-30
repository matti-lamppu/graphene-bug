from django.db import models


class FooType(models.TextChoices):
    FOO = "FOO", "Foo"
    BAR = "BAR", "Bar"
    BAZ = "BAZ", "Baz"


class Foo(models.Model):
    type = models.CharField(max_length=3, choices=FooType.choices)
