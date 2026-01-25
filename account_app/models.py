from datetime import timezone
from django.db import models

from django.contrib.auth.models import AbstractUser
# from django.db import models


# class Designation(models.Model):
#     Manager_CHOICES = [
#                             ('it_manager', 'IT Manager'),
#                             ('product_manager', 'Product Manager'),
#                             ('asistant_manager', 'Asistant Manager'),
#                       ]
#     Employee_CHOICES = [
#                             ('frontend', 'Frontend Developer'),
#                             ('backend', 'Backend Developer'),
#                             ('uiux', 'UI UX'),
#                             ('digital_market', 'Digital Marketing'),
#                         ]
#     DOMAIN_CHOICES=[('manager',Manager_CHOICES),('employee',Employee_CHOICES)]
    
#     title=models.CharField(max_length=50 , choices=DOMAIN_CHOICES)

#     def __str__(self):
#         return self.title
    
class ManagerDomain(models.Model):
    title=models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.title
    
class EmployeeDomain(models.Model):
    title=models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.title

  
class User(AbstractUser):
    # Role constants
    EMPLOYEE = 'employee'
    MANAGER = 'manager'
    # Role choices
    ROLE_CHOICES = [(EMPLOYEE, 'Employee'),(MANAGER, 'Manager')]
  
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True,blank=True)
    designation_m = models.ForeignKey(ManagerDomain , on_delete=models.CASCADE , related_name='manager_domain', null=True , blank=True)
    designation_e = models.ForeignKey(EmployeeDomain , on_delete=models.CASCADE , related_name='emp_domain', null=True , blank=True)
    gender = models.CharField(max_length=50)
    date_joined = models.DateField(null=True, blank=True)
    yop = models.DecimalField(max_digits=4,decimal_places=2, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile/',null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] 

    def __str__(self):
        return self.email 


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.email} (Expires: {self.expired_at})"

class OTP(models.Model):
    otp=models.CharField(max_length=6)
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='otp')   
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user} -> {self.otp}"
    




