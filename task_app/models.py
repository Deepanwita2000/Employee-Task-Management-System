from django.db import models
# from django.contrib.auth.models import User
from account_app.models import User
from project_app.models import Project
# Create a normal user
class Task(models.Model):
    PENDING = 'pending'
    PROGRESS = 'in progress'
    COMPLETED = 'completed'

    # Role choices
    ROLE_CHOICES = [
        (PENDING, 'Pending'),
        (PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=500) # manager will instruct some task to dev
    description = models.TextField() # manager will instruct some task to dev
    assigned_to = models.ForeignKey(User , on_delete=models.CASCADE,related_name='task_assigned' ) # employee
    assigned_by = models.ForeignKey(User , on_delete=models.CASCADE,related_name='task_create' ) # manager
    status = models.CharField(max_length=50, choices=ROLE_CHOICES)
    project = models.ForeignKey(Project , on_delete=models.CASCADE , related_name='task_project') # project file will be stored
    end_date = models.DateField()
    
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    #  title, description, assigned_to (ForeignKey → Employee), assigned_by (ForeignKey → User), status (choices: Pending/In Progress/Completed), created_at, updated_at


class Progress(models.Model):
    employee=models.ForeignKey(User , on_delete=models.CASCADE,related_name='progress_status' ) # employee
    value = models.DecimalField(max_digits=5 , decimal_places=2)
    task = models.ForeignKey(Task , on_delete=models.CASCADE,related_name='progress_task' ) # employee
    track_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} -> {self.value} -> {self.track_date}"