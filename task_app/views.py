from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from rest_framework.viewsets import ModelViewSet
from .models import Task
from .serializers import TaskSerializer
from account_app.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.decorators import action
from account_app.permissions import IsEmployee,IsManager
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse  
from account_app.models import User
from django.contrib.auth.decorators import login_required
from account_app.decorators import jwt_required
from django.contrib import messages
from .decorators import role_required
from django.views.decorators.csrf import csrf_exempt
# from comment_app.models import Comment
# from comment_app.serializers import CommentSerializer  
from django.views.decorators.http import require_POST

from task_app.models import Task
from django.db.models import Count
from django.utils import timezone

from django.db.models.query import QuerySet
from project_app.models import Project
from team_app.models import Team
from task_app.models import Progress
from account_app.serializers import UserSerializer
from django.core.paginator import Paginator


# ___________________________________for matplotlib
import matplotlib
matplotlib.use('Agg')  # Required for Django (no GUI)

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from .models import Progress


# Create your views here.
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()             # This will be used for listing and retrieving courses
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Create a course
    def perform_create(self, serializer):
        user = self.request.user  
        print(user)          # ModelViewSet → GenericViewSet → APIView that has request.user & request.data
        if user.role != 'manager':        # Only manager can create
            raise PermissionDenied("Only manager can aasigned")
        title = serializer.validated_data.get('title')
        employee_email = serializer.validated_data.get('employee_email')
        employee = User.objects.get(email=employee_email)
        print(f'details employee : {employee} | {employee.id}')

        
        if Task.objects.filter(assigned_by=user , assigned_to=employee.id).count() > 4:
            raise PermissionDenied("U cannot assign task to same employee more than 5")

        if Task.objects.filter(title=title , assigned_by=user).exists():
            raise ValidationError("employee with this title already exists.")
        serializer.save(assigned_by=user)

    @action(detail=False, methods=['get'], url_path='my-tasks', permission_classes=[IsEmployee])
    def my_tasks(self, request):
        user = request.user
        print(user)
        if user.role != 'employee':
            raise PermissionDenied("Only employees can access their own task.")
        
        tasks = Task.objects.filter(assigned_to=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    # view list of projects assigned by admin to manager
    @action(detail=False, methods=['get'], url_path='my-projects', permission_classes=[IsManager])
    def my_projects(self,request):
        user = request.user
        print(user,user.id)
        user_info=User.objects.get(id=user.id)
        teams= Team.objects.filter(manager=user_info)
        print(teams)
        my_data = [{'id':t.id , 'project':t.project.title , 'description':t.description , 'start_date':t.start_date , 'end_date':t.end_date } for t in teams]
            
        print(my_data)
        return Response({"my_data":my_data})
    
    # view project details
    @action(detail=True, methods=['get'],  permission_classes=[IsManager])
    def read_project(self,request,pk=None):
        project=Project.objects.get(id=pk)
        user = request.user
        print(user,user.id)
        print(project)
        try:
            assigned_manager= Team.objects.get(project=project , manager=user.id)
        except Team.DoesNotExist:
            return Response("Oops!!You are not assigned to this project.")
        file_url = request.build_absolute_uri(project.project_file.url) if project.project_file else None
        manager_name=assigned_manager.manager.first_name + " "+ assigned_manager.manager.last_name
        return Response({"id":project.id , "title":project.title , "description":project.description,"file":file_url , "Manager":manager_name})

    # no.of projects manager has been assigned
    @action(detail=False, methods=['get'],  url_path='project-count' ,permission_classes=[IsManager])
    def project_count(self,request):
        user=request.user
        # if user.role == 'employee':
        print(user , type(user))
        team=Team.objects.filter(manager = user)
        print(team)
        count=0
        for tm in team:
            print(tm.project)
            count=count+1
        return Response({"No.Of Projects ": count})
    
    @action(detail=False , methods=['GET'] , url_path='all-employees' , permission_classes=[IsManager])
    def all_employees(self,request):
        user=request.user
        if user.role !='manager':
            return PermissionDenied("user not valid")

        employees=User.objects.filter(role='employee')
        emp_serializer=UserSerializer(employees,many=True).data   # cnvert queryset to python native data
        # print(emp_serializer)
        return Response({'all-employees':emp_serializer})

    
    #################################### Employee's###########################################################
    @action(detail=False, methods=['get'],  url_path='my-project-count' ,permission_classes=[IsEmployee])
    def my_project_count(self,request):
        user=request.user
        # if user.role == 'employee':
        print(user , type(user))
        task=Task.objects.filter(assigned_to = user)
        print(task)
        count=0
        for t in task:
            print(t.project)
            count=count+1
        return Response({"No.Of Projects ": count})
        
    # @action(detail=True, methods=['get'],  permission_classes=[IsManager])
    # def view_proj_detail(self,request,pk=None):
    #     project=Project.objects.get(id=pk)
    #     user = request.user
    #     print(user,user.id)
    #     print(project)
    #     try:
    #         task= Task.objects.filter(project=project , manager=user.id)
    #     except Team.DoesNotExist:
    #         return Response("Oops!!You are not assigned to this project.")
    #     file_url = request.build_absolute_uri(project.project_file.url) if project.project_file else None
    #     manager_name=assigned_manager.manager.first_name + " "+ assigned_manager.manager.last_name
    #     return Response({"id":project.id , "title":project.title , "description":project.description,"file":file_url , "Manager":manager_name})

    




    # to give review
    @action(detail=True , methods=['POST'] , url_path='my-comment', permission_classes=[IsManager])
    def my_comment(self,request,pk=None):
        user=request.user
        print(user, user.role) # manager
        if user.role != 'manager':
            raise PermissionDenied("Only manager will able to rate ")
        task = self.get_object()
        print(task  , task.status)
       
        # if booking.status != 'going':
        #     raise PermissionDenied("U are not allowed to rate")
        comment = request.data['comment_text']
        
        Comment.objects.create(comment_text=comment ,  commented_by=user , task=task)
        return Response({"message":"reviews successfull"})


 
# # using query param
@api_view(['GET'])
@permission_classes([IsEmployee])
@authentication_classes([JWTAuthentication])
def serach_by_employee_id(request, pk=None):
        user = request.user
        tasks = Task.objects.filter(assigned_to=pk)
        print("inside serach_by_employee_id() : ",tasks)
        serializer = TaskSerializer(tasks , many=True)
        return Response({
                "data":"My  tasks",
                "tasks":serializer.data
            })
















##################################################### AJAX ####################################################

@login_required
@role_required('manager')
def get_task_rows(request):
    tasks= Task.objects.all()
    html = render_to_string('task_app/partial_task_list.html', {"tasks": tasks, "user": request.user})
    return JsonResponse({"html": html})


# def read_task(request):
#     tasks = Task.objects.all()
#     print(tasks)
#         # subjects = Subject.objects.select_related("stream")  # Use select_related for optimization
#     # html_string = render_to_string("task_app/task_rows.html", {"tasks": tasks})
#     # task_data = 
#     return render(request ,'task_app/create_task.html',  {"tasks": tasks, "message": "tasks saved successfully!"})  

@jwt_required
@role_required('manager')
def create_task(request):
    # status = Task.objects.all()
    user = request.user
    print("Inside create_task :--------> ",user)
    if request.method == 'GET':
        print(Task.ROLE_CHOICES)
        tasks :QuerySet= Task.objects.all()
        teams :QuerySet= Team.objects.filter(manager=user)
        for i in teams:
            print(f"|{i.manager} -> {i.employee}|")
       
        return render(request , 'task_app/create_task.html' , {"status":Task.ROLE_CHOICES , "tasks":tasks , "teams":teams})
    # if request.method == "POST":
    #     title = request.POST.get('title')
    #     description = request.POST.get('description')
    #     status = request.POST.get('status')
    #     emp_email = request.POST.get('emp_email')

    #     # if User.objects.get(email=emp_email).exist():
    #     try:
    #         employee = User.objects.get(email=emp_email)
    #     except User.DoesNotExist:
    #          return JsonResponse({'message':f"{emp_email} : Not a registered email id"}, status=400)
    #     print("employee : ",employee)
    #     print("request.user : ",request.user)
    #     # if not employee:
    #     #     return JsonResponse({'message':f"Error: {emp_email} does not exists"}, status=400)
    #     if Task.objects.filter(assigned_to = employee,assigned_by=request.user , title=title).exists():
    #         print("same task cannot be alloted to same employee twice")
    #         return JsonResponse({'message':"same title cannot be alloted to the same employee twice"}, status=400)

    #     if Task.objects.filter(assigned_to = employee,assigned_by=request.user).count() > 4:
    #         print("U cannot assign task to same employee more than 5 times")
    #         return JsonResponse({'message':"U cannot assign task to same employee more than 5"}, status=400)

    #     task = Task.objects.create(title=title,
    #                         description=description,
    #                         assigned_to = employee,
    #                         assigned_by=request.user,
    #                         status=status)
    #     task.save()
    #     print(task)
    #     print(f"task {title} created by {request.user.username}")

    #     tasks = Task.objects.all()
    #     task_data = [{'title':task.title , 'description':task.description , 'status':task.status , 'assigned_to':task.assigned_to.username,
    #                   'assigned_by':task.assigned_by.username} for task in tasks] 
    #     return JsonResponse({
    #         'tasks': task_data, 
    #         'message': 'task created successfully!'})
    # else:
    #     tasks = Task.objects.all()
    # return render(request, 'task_app/create_task.html', {'tasks': tasks})

# @login_required 
# @jwt_required
# @role_required('manager')
# @require_POST
# def edit_task(request, task_id):
#     task = get_object_or_404(Task, id=task_id)
#     print(task)

#     # Allow only the organizer who created the program to edit
#     if task.assigned_by != request.user:
#         return JsonResponse({'error': 'You are not allowed to edit this task.'}, status=403)

#     title = request.POST.get('title')
#     description = request.POST.get('description')
#     status = request.POST.get('status')
#     emp_email = request.POST.get('emp_email')
#     new_employee = User.objects.get(email=emp_email)
#     print(title,description,status,new_employee)

#     if not title or not description:
#         return JsonResponse({'error': 'Title and description are required.'}, status=400)

#     task.title = title
#     task.description = description
#     task.status = status
#     task.assigned_to = new_employee
#     task.save()

#     return JsonResponse({'message': 'task updated successfully!'})


@login_required
@role_required('manager', 'employee')
def program_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_app/task_list.html', {'tasks': tasks})


@login_required
@role_required('employee')
def emp_task_list(request):
    print(request.user.role)
    tasks = Task.objects.all()
    print(tasks)
    return render(request, 'task_app/emp_task_list.html', {'tasks': tasks , 'user':request.user})


# @csrf_exempt
# @require_POST
# @jwt_required
# @role_required('employee')
# def update_status(request):
#     if request.method == 'POST':
#         taskID = request.POST.get("taskID")
#         current_status = request.POST.get("current_status")
#         print(taskID , current_status)
#         getTask = Task.objects.get(id = taskID)
#         print(getTask , getTask.status)
#         getTask.status = current_status
#         getTask.save()
#         print("******************* update_status *******************************")
#         print("getTask-> ",getTask)
#         userInfo = User.objects.get(email=request.user)
#         print(userInfo)
#         tasks = Task.objects.filter(assigned_to=userInfo)
#         task_data = [{'title':task.title , 'description':task.description , 'status':task.status , 'assigned_to':task.assigned_to.username,
#                       'assigned_by':task.assigned_by.username} for task in tasks] 
#         print(task_data)
#         return JsonResponse({
#             'tasks': task_data, 
#             'message': 'task saved successfully!'})


@login_required
@role_required('employee')
def get_task_rows_employee(request):
    # tasks= Task.objects.all()
    userInfo = User.objects.get(email=request.user)
    print(userInfo)
    tasks = Task.objects.filter(assigned_to=userInfo)
    html = render_to_string('task_app/partial_task_list.html', {"tasks": tasks, "user": request.user})
    print("******************* get_task_rows_employee *******************************")
    print(html)
    return JsonResponse({"html": html})


# show all employees
@login_required
@role_required('manager')
def all_employees_completed(request):
    user = request.user
    print(user,user.role)
    if user.role != 'manager':
        return JsonResponse("Only managers are allowed to see")
    # completed_tasks = Task.objects.filter(status='completed')
    # to filter in specific months
    # completed_tasks = Task.objects.filter(status='completed' , updated_at__month=11)
    completed_tasks = Task.objects.all()
    print(completed_tasks)
    # return HttpResponse(completed_tasks)
    return render(request , 'employee_app/emp_task_details.html' , {"tasks":completed_tasks , "all_managers":True})

# show all employees who has completed more than 3 tasks in current mnth
@login_required
@role_required('manager')
def best_employees(request):
    now = timezone.now()
    print(now)

    # Fetch employees with more than 3 completed tasks this month
    employees = (
        Task.objects.filter(
            status='completed',
            updated_at__month=now.month,
            updated_at__year=now.year
        ).values('assigned_to__id', 'assigned_to__email', 'assigned_to__first_name', 'assigned_to__last_name','assigned_to__designation')
        .annotate(total_completed=Count('id'))
        .filter(total_completed__gt=3)
        .order_by('-total_completed')
    )
    # employees = (Task.objects.filter(status='completed', updated_at__month=now.month,updated_at__year=now.year).values('assigned_to').annotate(completed_count=Count('id')).filter(completed_count__gte=3))
    print(employees)

    return render(request, 'employee_app/best_employees.html', {'employees': employees})

#//////////////////////////////////////////////////////// Renew/////////////////////////////////////////////////////////////////
@login_required
@role_required('manager','employee')
def view_projects(request):
    user=request.user
    print(user)
    if user.role == 'manager':
        title=set()
        my_projects = Team.objects.filter(manager=user)
        print(my_projects)
        for i in my_projects:
            title.add((i.project,i.project.id))
        return render(request , 'manager/project/view_projects.html',{"title" :title})
    elif user.role == 'employee':
        title=set()
        my_projects = Task.objects.filter(assigned_to=user)
        print(my_projects)
        for i in my_projects:
            title.add((i.project,i.project.id))
        return render(request , 'manager/project/view_projects.html',{"title" :title})

@login_required
@role_required('manager','employee')
def view_project_details(request,proj_id=None):
    user=request.user
    proj = get_object_or_404(Project,id=proj_id) if proj_id else None
    print("inside view details :   -----------------")
    print(proj.title , proj.id , proj.project_file)
    if user.role == 'manager':
        teams = Team.objects.filter(manager=user,project=proj)
        print(teams)
        context={
            "title":proj.title,
            "file":proj.project_file, # contains project document file 
            "description":proj.description,
            "teams":teams,
            "user":user,
            "project_id":proj.id

        }
        return render(request , 'manager/project/view_project_details.html' , context)
    elif user.role == 'employee':
        tasks = Task.objects.filter(assigned_to=user , project=proj)
        # alloted_proj=Project.objects.get()
        print(tasks)
        context={
            "title":proj.title,
            "file":proj.project_file, # contains project document file 
             "description":proj.description,
             "tasks":tasks,
             "user":user,
            "project_id":proj.id,
            "project":proj

        }
        return render(request , 'manager/project/view_project_details.html' , context)

@login_required
@role_required('manager')    
def view_task_form(request ,proj_id=None):
    proj = get_object_or_404(Project , id=proj_id) if proj_id else None
    print(proj)
    user = request.user
    print("Inside view_task_form :--------> ",user , proj , type(proj))
   
    print(Task.ROLE_CHOICES)
    tasks :QuerySet= Task.objects.filter(project=proj)
    teams :QuerySet= Team.objects.filter(manager=user)
    employees = User.objects.filter(role='employee')
    print(employees)
    for i in teams:
        print(f"|{i.manager} -> {i.project.title}|")
    
    context={
        "project":proj,
        "status":Task.ROLE_CHOICES,
        "employees":employees,
        "tasks":tasks
    }
    return render(request , 'task_app/add_employee.html',context)

@login_required
@role_required('manager')
def add_task(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        employee = request.POST.get('employee')
        project_id = request.POST.get('project')
        end_date = request.POST.get('end_date')
        # print(project , type(project))
        project = get_object_or_404(Project , id=project_id) if project_id else None
        # if User.objects.get(email=emp_email).exist():
        try:
            employee = User.objects.get(email=employee)
        except User.DoesNotExist:
             return JsonResponse({'message':f"{employee} : Not a registered email id"}, status=400)
        print("employee : ",employee)
        print("request.user : ",request.user)
        # if not employee:
        #     return JsonResponse({'message':f"Error: {emp_email} does not exists"}, status=400)
        if Task.objects.filter(assigned_to = employee,assigned_by=request.user , title=title, project=project).exists():
            print("same task cannot be alloted to same employee twice")
            return JsonResponse({'message':"same title cannot be alloted to the same employee twice"}, status=400)

        if Task.objects.filter(assigned_to = employee,assigned_by=request.user).count() > 4:
            print("U cannot assign task to same employee more than 5 times")
            return JsonResponse({'message':"U cannot assign task to same employee more than 5"}, status=400)

        task = Task.objects.create(title=title,
                            description=description,
                            assigned_to = employee,
                            assigned_by=request.user,
                            status=status,
                            project=project,
                            end_date=end_date
                            )
        messages.success(request, "Task added successfully!")
        task.save()
        print(task)
        print(f"task {title} created by {request.user.username}")

        tasks = Task.objects.all()
        tasks_html = render_to_string('task_app/partials/task_rows.html',{"tasks":tasks , "user": request.user})
        print(tasks_html)
        return JsonResponse({
            'tasks': tasks_html, 
            'message': 'task created successfully!'})
    else:
        # proj = get_object_or_404(Project , id=proj_id) if proj_id else None
        # print(proj)
        user = request.user
        # print("Inside view_task_form :--------> ",user , proj , type(proj))
        
        print(Task.ROLE_CHOICES)
        tasks :QuerySet= Task.objects.all()
        teams :QuerySet= Team.objects.filter(manager=user)
        employees = User.objects.filter(role='employee')
        print(employees)
        for i in teams:
            print(f"|{i.manager} -> {i.project.title}|")
        context={
            # "project":proj,
            "status":Task.ROLE_CHOICES,
            "employees":employees,
            "tasks":tasks
             }
        
        
    return render(request, 'task_app/create_task.html', {'context': context})

@jwt_required
@role_required('manager')
@require_POST
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    print(task)

    # Allow only the organizer who created the program to edit
    if task.assigned_by != request.user:
        return JsonResponse({'error': 'You are not allowed to edit this task.'}, status=403)

    title = request.POST.get('title')
    description = request.POST.get('description')
    status = request.POST.get('status')
    emp_email = request.POST.get('employee')
    new_employee = User.objects.get(email=emp_email)
    print(title,description,status,new_employee)

    if not title or not description:
        return JsonResponse({'error': 'Title and description are required.'}, status=400)

    task.title = title
    task.description = description
    task.status = status
    task.assigned_to = new_employee
    task.save()
    print(task)
    print(f"task {title} created by {request.user.username}")

    tasks = Task.objects.all()
    tasks_html = render_to_string('task_app/partials/task_rows.html',{"tasks":tasks , "user": request.user})
    print(tasks_html)
    return JsonResponse({
        'tasks': tasks_html, 
        'message': 'task updated successfully!'})

    # return JsonResponse({'message': 'task updated successfully!'})

@jwt_required
@role_required('manager')
@require_POST
def delete_task(request , task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.assigned_by != request.user:
        return JsonResponse({'error': 'You are not allowed to delete this task.'}, status=403)
    
    task.delete()
    return JsonResponse({'message': 'task deleted successfully!'})

@role_required('manager')
@login_required
def view_progress(request , user_id=None):
    user=request.user
    userInfo=get_object_or_404(User , id=user_id) if user_id else None
    user_progress :QuerySet = Progress.objects.filter(employee=user_id)
    print(user_progress)
    print(userInfo.id)
    return render(request , 'progress/prog_data.html',{"user_progress":user_progress , "user_id":user_id})

@login_required
@role_required('manager')
def employee_line_graph(request, employee_id):
    # Get progress data for this employee
    progress = Progress.objects.filter(employee_id=employee_id).order_by("track_date")

    # Extract x and y values
    dates = [p.track_date for p in progress]
    values = [p.value for p in progress]

    # Create graph
    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker='o', linewidth=2)
    plt.title("Employee Progress (Date vs Value)")
    plt.xlabel("Date")
    plt.ylabel("Progress (%)")
    plt.grid(True)
    plt.tight_layout()

    # Save to memory
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()      # prevents memory leak
    buffer.seek(0)

    # Convert plot to base64
    graph_png = buffer.getvalue()
    graph = base64.b64encode(graph_png).decode('utf-8')
    buffer.close()

    # Render HTML
    return render(request, "progress/employee_progress_graph.html", {"graph": graph})

# view all employess
# @login_required
# @role_required('manager')
# def employee_list(request):
#     all_employees = User.objects.filter(role='employee').order_by('date_joined')
#     emp_count = all_employees.count()
#     print(all_employees , emp_count) 

#     # pagination
#     paginator = Paginator(all_employees , per_page=5 )  # can add  orphans=1 if any extra row remains that will get adjusted in the last page
#     page_number = request.GET.get('page')
#     page_obj= paginator.get_page(page_number)
#     print("Page number : ",page_number)
#     print("Page obj : ",page_obj)

#     return render(request , 'employee_app/all_employees.html' , {"page_obj":page_obj ,  "emp_count":emp_count})

@login_required
@role_required('manager')
def employeeList_pending_status(request):
    user=request.user #manager
    tasks=Task.objects.filter(assigned_by=user , status='pending')
    pending_count=tasks.count()
    return render(request , 'employee_app/employee_per_status.html',{"tasks":tasks , "pending_count":pending_count})

@login_required
@role_required('manager')
def employeeList_progress_status(request):
    user=request.user #manager
    tasks=Task.objects.filter(assigned_by=user , status='in progress')
    progress_count=tasks.count()
    return render(request , 'employee_app/employee_per_status.html',{"tasks":tasks , "progress_count":progress_count})

@login_required
@role_required('manager')
def employeeList_complete_status(request):
    user=request.user #manager
    tasks=Task.objects.filter(assigned_by=user , status='completed')
    return render(request , 'employee_app/employee_per_status.html',{"tasks":tasks})

# -------------------------- functions where employee can access ------------------------------------ #

# to see teams members under assigned proj
@login_required
@role_required('employee')    
def view_team_members(request , proj_id=None):
    proj=get_object_or_404(Project , id=proj_id) if proj_id else None
    user = request.user
    tasks = Task.objects.filter(project=proj)
    print("view tasks under assihned project" , tasks)
    return render(request , 'employee_app/team_members.html' , {'tasks':tasks})

# to see teams members under assigned proj
@login_required
@role_required('employee')    
def view_alloted_task(request):
    user = request.user
    if user.role != 'employee':
        pass
           
    tasks = Task.objects.filter(assigned_to=user)
    print(f"tasks alloted to current user :{user} -> {tasks}")
    return render(request , 'employee_app/view_assigned_task.html',{"tasks":tasks})

@csrf_exempt
@login_required
@role_required('employee')    
def update_status(request, id, status):
    user = request.user

    try:
        task = Task.objects.get(id=id, assigned_to=user)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    # Convert status key to readable status
    if status == "completed":
        task.status = "completed"
    elif status == "in_progress":
        task.status = "in progress"      # your DB stores space version
    else:
        return JsonResponse({"error": "Invalid status"}, status=400)

    task.save()

    # return JsonResponse({"success": True, "status": task.status})
    tasks = Task.objects.filter(id=task.id,assigned_to=user)
    task_html=render_to_string('task_app/partials/task_rows.html', {'tasks':tasks , 'user':user , 'status':status})
    print(task_html)
    return JsonResponse({"success": True , 'tasks':task_html , 'status':status})
# return JsonResponse({"success": False})

@csrf_exempt
@login_required
@role_required('employee')  
def analyze_progress(request):
    user=request.user
    if request.method == 'POST':
        task_id=request.POST.get("task_id")
        value = request.POST.get("progress_value") 
        print(task_id,value)
    if Task.objects.filter(id=task_id , assigned_to=user).exists():
        task=Task.objects.get(id=task_id)
        p=Progress.objects.create(employee=user,task=task, value=value)
        p.save()
    return JsonResponse({"message":f"progress updated to {value}% "})

@login_required
@role_required('employee')          
def myTodo(request):
    return render(request , 'profile/todo.html')


#---------------------------------------------------- checkng purpose
# view all employess
@login_required
@role_required('manager')
def employee_list(request):
    all_employees = User.objects.filter(role='employee').order_by('date_joined')
    emp_count = all_employees.count()
    print(all_employees , emp_count) 

    # pagination
    paginator = Paginator(all_employees , per_page=5 )  # can add  orphans=1 if any extra row remains that will get adjusted in the last page
    page_number = request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    print("Page number : ",page_number)
    print("Page obj : ",page_obj)

    return render(request , 'employee_app/all_employees.html' , {"page_obj":page_obj ,  "emp_count":emp_count})