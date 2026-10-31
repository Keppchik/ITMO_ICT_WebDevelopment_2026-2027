from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Hotel, RoomType, Room, Facility, Reservation, Stay, Review

# Register your models here.
admin.site.register(get_user_model())
admin.site.register(Hotel)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Facility)
admin.site.register(Stay)
admin.site.register(Review)
admin.site.register(Reservation)