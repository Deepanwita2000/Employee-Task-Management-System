from django.db import models
from project_app.models import Project
from account_app.models import User,EmployeeDomain
# Create your models here.
class Task2(models.Model):
    tasks=models.JSONField(default=list)  # [task1 , task2 , task3, ...]
    # domain = models.CharField(max_length=200)
    domain = models.ForeignKey(EmployeeDomain , on_delete=models.CASCADE , related_name='task2')
    project= models.ForeignKey(Project , on_delete=models.CASCADE , related_name='task2')
    manager= models.ForeignKey(User , on_delete=models.CASCADE , related_name='task2')
    end_date=models.DateField()

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.domain} : {self.project}"
    

class AssignEmployee(models.Model):
    PENDING = 'pending'
    PROGRESS = 'in progress'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]
    task=models.ForeignKey(Task2 , on_delete=models.CASCADE , related_name='task2')
    assigned_to = models.ForeignKey(User , on_delete=models.CASCADE , related_name='assignment_emp')
    assigned_by = models.ForeignKey(User , on_delete=models.CASCADE , related_name='assignment_mng')
    project=models.ForeignKey(Project , on_delete=models.CASCADE , related_name='assignment')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    is_complete = models.BooleanField(default=False , blank=True , null=True)

    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assigned_to} : {self.project}"

    
class Progress(models.Model):
    task = models.CharField(blank=True , null=True) # employee
    status = models.CharField(default='progress') 
    point = models.DecimalField(max_digits=5 , decimal_places=2, default=10.0)
    date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey(User , on_delete=models.CASCADE,related_name='progress' ) 
    project = models.ForeignKey(Project , on_delete=models.CASCADE , related_name='progress')
    domain = models.ForeignKey(EmployeeDomain , on_delete=models.CASCADE , related_name='progress')
    complete_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False , blank=True , null=True)

    def __str__(self):
        return f"{self.employee.username} -> {self.point}"
    

class Update(models.Model):
    total_points=models.DecimalField(default=0.0,max_digits=5,decimal_places=2)
    percentage=models.DecimalField(default=0.0,max_digits=5,decimal_places=2)
    status = models.CharField(default='progress') # status=complete
    employee = models.ForeignKey(User , on_delete=models.CASCADE,related_name='update') 
    project = models.ForeignKey(Project , on_delete=models.CASCADE , related_name='update')
    manager = models.ForeignKey(User , on_delete=models.CASCADE , related_name='assigned_by')
    def __str__(self):
        return f"{self.employee.username} -> {self.total_points}"