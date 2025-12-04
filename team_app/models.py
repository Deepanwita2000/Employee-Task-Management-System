from django.db import models
from account_app.models import User
from project_app.models import Project
# Create your models here.
class Team(models.Model):
    project =  models.ForeignKey(Project,on_delete=models.CASCADE,related_name='team_title')
    description = models.TextField(null=True , blank=True)
    manager = models.ForeignKey(User , on_delete=models.CASCADE ,limit_choices_to={'role': 'manager'}, related_name='team_manager')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True , blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.manager} - {self.project.title}"


