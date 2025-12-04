from django.db import models
from task_app.models import Task
from account_app.models import User
# Create your models here.
class Comment(models.Model):
    task = models.ForeignKey(Task , on_delete=models.CASCADE , related_name='task_comment')
    comment_text = models.TextField()
    commented_by = models.ForeignKey(User , on_delete=models.CASCADE , related_name="comment_manager") # manager
    commented_to = models.ForeignKey(User , on_delete=models.CASCADE , related_name="comment_employee") # employee
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} commented by -{self.commented_by} "

    


# •	TaskComment
# Fields: task (ForeignKey → Task), comment_text, commented_by (ForeignKey → User), commented_at
  