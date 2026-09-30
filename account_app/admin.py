from django.contrib import admin
from .models import User,ManagerDomain,EmployeeDomain

# Register your models here.

class UserDetails(admin.ModelAdmin):
    list_display=[
        "id",
    'role',
    'first_name',
    'last_name',
    'email',
    
    'date_joined',
    ]
    search_fields = [
       
        'role',
      
    ]
    list_filter = (
        'role',
        'date_joined',
        'designation_e',
        'designation_m',
    )
admin.site.register(User,UserDetails)  

from django.contrib.auth.admin import UserAdmin



@admin.register(ManagerDomain)
class ManagerDomainDetails(admin.ModelAdmin):
    list_display=[
        'id',
    'title',
    
    ]


@admin.register(EmployeeDomain)
class EmpDomainDetails(admin.ModelAdmin):
    list_display=[
        'id',
    'title',
    
    ]
