from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    passport_number = models.CharField(max_length=10, blank=True)
    nationality     = models.CharField(max_length=30, blank=True)
    home_address    = models.CharField(max_length=100, blank=True)


class Car(models.Model):
    id_owners  = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Ownership')
    gos_number = models.CharField(max_length=15)
    brand      = models.CharField(max_length=20)
    model      = models.CharField(max_length=20)
    color      = models.CharField(max_length=30)

class Ownership(models.Model):
    id_carOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id_car      = models.ForeignKey(Car, on_delete=models.CASCADE)
    date_start  = models.DateTimeField()
    date_end    = models.DateTimeField()

class DriverLicense(models.Model):
    CATEGORY_CHOICES = [
        ('A', 'A — мотоциклы'),
        ('B', 'B — легковые'),
        ('C', 'C — грузовые'),
        ('D', 'D — автобусы'),
        ('BE', 'BE — легковые с прицепом'),
        ('CE', 'CE — грузовые с прицепом'),
        ('DE', 'DE — автобусы с прицепом'),
    ]

    id_carOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    number      = models.CharField(max_length=10)
    type        = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    issue_date  = models.DateTimeField()

