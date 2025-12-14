from django.shortcuts import render,get_object_or_404
from task_app.models import Task
from comment_app.models import Comment
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from account_app.decorators import jwt_required
from task_app.decorators import role_required
# Create your views here.
  
@jwt_required
@role_required('manager')
def create_comment(request , pk=None):
    user=request.user
    print(request.user)
    task = get_object_or_404(Task , pk=pk) if pk else None
    comm = Comment.objects.filter(task=task , commented_by=request.user)
    print(comm)
    taskID=task.id
    empployee=task.assigned_to
    if request.method == 'POST':
        com_id = request.POST .get("com_id")
        com_text = request.POST .get("com_text")
        print("create_comment_pro : ",taskID,com_id , com_text,empployee)
        
        Comment.objects.create(task=task , comment_text=com_text , commented_by=user , commented_to=empployee)
        
        # comments = Comment.objects.all()
        comm = Comment.objects.filter(task=task , commented_by=request.user)
        html_data = render_to_string('comment/partial_comment.html' , {"comments":comm , "user":user})
        # print(html_data)
        return JsonResponse({"comments":html_data})

    return render(request , 'comment/create_comment.html' , {"id":task.id  , "comments":comm , "user":user})



@login_required
@role_required('employee')
def view_messages(request):
    user=request.user

    com = Comment.objects.filter(commented_to=user)
    print(com)
    return render(request , 'employee_app/view_message.html', {'comments':com , 'user':user})

