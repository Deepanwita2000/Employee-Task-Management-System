from django.contrib import admin


from .models import User
# Register your models here.

class UserDetails(admin.ModelAdmin):
    list_display=[
    'role',
    'first_name',
    'last_name',
    'email',
    'designation',
    'date_joined',
    ]
admin.site.register(User,UserDetails)  