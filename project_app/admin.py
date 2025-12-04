from django.contrib import admin

# Register your models here.
from .models import Project
# Register your models here.

class ProjectDetails(admin.ModelAdmin):
    list_display=[
    'title',
    'description',
    'project_file',
    'created_at',
    'updated_at'

    ]
admin.site.register(Project,ProjectDetails)  