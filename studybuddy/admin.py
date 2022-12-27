from django.contrib import admin

# Register your models here.
#ev


from .models import User, Room

admin.site.register(User)
admin.site.register(Room)