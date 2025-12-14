from django.contrib import admin

# Register your models here.
from .models import Team
# Register your models here.

class TeamDetails(admin.ModelAdmin):
    list_display=[
    'manager',
 
    'project',
    'start_date',
    'end_date',
    'updated_at'

    ]
admin.site.register(Team,TeamDetails)  