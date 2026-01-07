from django.contrib import admin


from .models import User,ManagerDomain,EmployeeDomain
# Register your models here.

class UserDetails(admin.ModelAdmin):
    list_display=[
    'role',
    'first_name',
    'last_name',
    'email',
    
    'date_joined',
    ]
admin.site.register(User,UserDetails)  



class ManagerDomainDetails(admin.ModelAdmin):
    list_display=[
    'title',
    
    ]
admin.site.register(ManagerDomain,ManagerDomainDetails) 



class EmpDomainDetails(admin.ModelAdmin):
    list_display=[
    'title',
    
    ]
admin.site.register(EmployeeDomain,EmpDomainDetails) 