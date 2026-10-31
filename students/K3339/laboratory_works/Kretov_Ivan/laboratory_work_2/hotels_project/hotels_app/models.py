from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    passport_number = models.CharField(max_length=10, blank=True, null=True)
    phone           = models.CharField(max_length=14, blank=True, null=True)
    birthday        = models.DateField(blank=True, null=True)
    nationality     = models.CharField(max_length=20, blank=True, null=True)
    address         = models.CharField(max_length=60, blank=True, null=True)

class Hotel(models.Model):
    name        = models.CharField(max_length=20)
    owner       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)
    city        = models.CharField(max_length=20)
    address     = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    stars       = models.PositiveSmallIntegerField()
    photo       = models.ImageField(upload_to='hotels/')

class Facility(models.Model):
    name        = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    icon        = models.ImageField(upload_to='facilities/')

class RoomType(models.Model):
    hotel       = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name        = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    capacity    = models.PositiveSmallIntegerField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    facilities   = models.ManyToManyField(Facility)
    photo       = models.ImageField(upload_to='rooms/')

class Room(models.Model):
    room_type    = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    number       = models.CharField(max_length=10)
    floor        = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('checked_in','Заселен'),
        ('checked_out','Выселен'),
        ('cancelled', 'Отменена'),
    ]

    guest        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room         = models.ForeignKey(Room, on_delete=models.PROTECT)
    date_from    = models.DateField()
    date_to      = models.DateField()
    guests_count = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    status       = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2)
    comments     = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.date_from and self.date_to and self.room:
            nights = (self.date_to - self.date_from).days
            self.total_price = nights * self.room.room_type.price
        super().save(*args, **kwargs)

class Stay(models.Model):
    guest          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_in_at  = models.DateTimeField()
    checked_out_at = models.DateTimeField(blank=True, null=True)
    room           = models.ForeignKey(Room, on_delete=models.PROTECT)

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    author            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stay              = models.ForeignKey(Stay, on_delete=models.SET_NULL, null=True)
    text              = models.TextField(blank=True, null=True)
    rating            = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at        = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Reservation)
def reservation_status_changed(sender, instance, created, **kwargs):
    if created:
        return

    if instance.status == 'checked_in':
        Stay.objects.get_or_create(
            guest=instance.guest,
            room=instance.room,
            checked_out_at__isnull=True,
            defaults={ 'checked_in_at': timezone.now(), },
        )

    elif instance.status == 'checked_out':
        Stay.objects.filter(
            guest=instance.guest,
            room=instance.room,
            checked_out_at__isnull=True,
        ).update(checked_out_at=timezone.now())