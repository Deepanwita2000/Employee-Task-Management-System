import os
import json
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.core.paginator import Paginator

from account_app.serializers import UserSerializer
from project_app.serializers import ProjecrSerializer

from .decorators import role_required
from .models import Task2,AssignEmployee,Progress,Update

from account_app.models import User
from account_app.models  import ManagerDomain,EmployeeDomain
from account_app.decorators import jwt_required

from project_app.models import Project

from team_app.models import Team

from langchain_groq import ChatGroq
from .serializers import TaskSerializer

from team_app.serializers import TeamSerializer

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from account_app.authentication import JWTAuthentication
from account_app.permissions import IsManager,IsEmployee,IsEmployeeOrManager

class TeamView(ModelViewSet):
    queryset = Team.objects.all()             # This will be used for listing and retrieving courses
    serializer_class = TeamSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsManager]

    @action(detail=False, methods=['get'], url_path='project-list', permission_classes=[IsManager])
    def project_list(self, request):
        user = request.user
        if user.role != 'manager': 
            raise PermissionDenied("Only manager can access their own projects.")

        teams = Team.objects.filter(manager=user)
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)
    
    
class TaskView(ModelViewSet):
    queryset = Task2.objects.all()             # This will be used for listing and retrieving courses
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    @action(detail=True, methods=['get'],  permission_classes=[IsEmployeeOrManager])
    def project_info(self,request , pk=None):
        # project=get_object_or_404(Project ,id=proj_id) if proj_id else None
        project = get_object_or_404(Project, id=pk)
        print(project)
        user =request.user
        print(user , type(user))
        if user.role == 'manager':
            try:
                assigned_manager= Team.objects.get(project=project , manager=user)
            except Team.DoesNotExist:
                return Response("Oops!!You are not assigned to this project.")
            file_url = request.build_absolute_uri(project.project_file.url) if project.project_file else None
            manager_name=assigned_manager.manager.first_name + " "+ assigned_manager.manager.last_name
            return Response({"id":project.id , "title":project.title , "description":project.description,"file":file_url , "Manager":manager_name})
        elif user.role == 'employee':
            if AssignEmployee.objects.filter(project=project ,  assigned_to =  user) .exists():
                file_url = request.build_absolute_uri(project.project_file.url) if project.project_file else None
            emp_name=user.first_name + " "+ user.last_name
            return Response({"id":project.id , "title":project.title , "description":project.description,"file":file_url , "Employee":emp_name})

    @action(detail=False , methods=['GET'] , url_path='all-employees' , permission_classes=[IsManager])
    def all_employees(self,request):
        user=request.user
        if user.role !='manager':
            return PermissionDenied("user not valid")

        employees=User.objects.filter(role='employee')
        emp_count=employees.count()
        print(employees)
        emp_serializer=UserSerializer(employees,many=True).data   # cnvert queryset to python native data
        # print(emp_serializer)
        return Response({'Employee Count':emp_count,'all-employees':emp_serializer})
     # view project details
    @action(detail=False , methods=['GET'] , url_path='my-projects' , permission_classes=[IsEmployee])
    def my_projects(self,request):
        user=request.user
        assign_employee=AssignEmployee.objects.filter(assigned_to=user)
        ct=0
        for i in assign_employee:
            context={'project':i.project.title , 'Manager':i.assigned_by.first_name+" "+i.assigned_by.last_name}
        return Response(context)

# ------------------------------------------------------------------- AJAX --------------------------------------------------------------------

@login_required
@role_required('manager','employee') # get list of projects alloted 
def view_projects(request):
    user=request.user
    print(user)
    if user.role == 'manager':
        title=set()
        my_projects = Team.objects.filter(manager=user)
        has_project=True if my_projects else None
        print(my_projects)
        for i in my_projects:
            title.add((i.project,i.project.id))
        return render(request , 'task2_app/list_projects.html',{"has_project":has_project,"title" :title})
    elif user.role == 'employee':
        title=set()
        # my_projects = Task.objects.filter(assigned_to=user)
        my_projects = AssignEmployee.objects.filter(assigned_to=user)
        
        has_project=True if my_projects else None

        print(my_projects)
        for i in my_projects:
            title.add((i.project,i.project.id))
        return render(request , 'task2_app/list_projects.html',{"has_project":has_project,"title" :title})
    
@login_required
@role_required('manager','employee')    # managers and employeees can see the project descr and download the file
def view_project_info(request,proj_id=None):
    user=request.user
    proj = get_object_or_404(Project,id=proj_id) if proj_id else None
    print("inside view details :   -----------------")
    print(proj.title , proj.id , proj.project_file)
    if user.role == 'manager':
        try:
            teams = Team.objects.filter(manager=user,project=proj)
            print("teams: ------------> ",teams)
            tm=Team.objects.get(manager=user , project=proj)
            print("team date:-----> ",tm.end_date)
            count_pending_tasks,count_complete_tasks,count_progress_tasks=0,0,0
            # 
            assgn_emps=AssignEmployee.objects.filter(assigned_by=user , project=proj)
                        
            # ----------------------pending
            seen=set()
            for e in assgn_emps:
                if not Update.objects.filter(employee=e.assigned_to,manager=user,project=proj).exists():
                    if e.assigned_to.username not in seen:
                        seen.add(e.assigned_to.username)
                        
            print(seen)
            count_pending_tasks=len(seen)
            # ----------------------progress
            progress=set()
            for e in assgn_emps:
                if  Update.objects.filter(employee=e.assigned_to,manager=user,percentage__lt=100,project=proj).exists():
                    print(e.assigned_to.username)
                    if e.assigned_to.username not in progress:
                        progress.add(e.assigned_to.username)
            print("progress --> ",progress)
            count_progress_tasks=len(progress)
            # ----------------------complete
            cmplte=set()
            for e in assgn_emps:
                if Update.objects.filter(employee=e.assigned_to,manager=user,percentage=100,project=proj).exists():
                    if e.assigned_to.username not in cmplte:
                        cmplte.add(e.assigned_to.username)
            print("cmplte --> ",cmplte)
            count_complete_tasks=len(cmplte)
            # 





            
            users = User.objects.filter(role="employee")
            context={
                "title":proj.title,
                "file":proj.project_file, # contains project document file 
                "description":proj.description,
                "teams":teams,
                "user":user,
                "project_id":proj.id,
                "users":users,
                "start_date":tm.start_date,
                "sub_date":tm.end_date,
                "count_pending_tasks":count_pending_tasks,
                "count_complete_tasks":count_complete_tasks,
                "count_progress_tasks":count_progress_tasks
            }
            return render(request , 'task2_app/project_Info.html' , context)
        except :
            message="<div class='alert alert-warning' role='alert'>This is a warning alert—check it out!</div>"
            return render(request , 'other/message.html')
        # return render(request , 'manager/project/view_project_details.html' , context)
        
    elif user.role == 'employee':
        # tasks = Task.objects.filter(assigned_to=user , project=proj)
        tasks = AssignEmployee.objects.filter(assigned_to=user , project=proj)
        tm=Team.objects.get(project=proj)
        # tm=Team.objects.get
        # alloted_proj=Project.objects.get()
        print(tasks)
        context={
            "title":proj.title,
            "file":proj.project_file, # contains project document file 
             "description":proj.description,
             "tasks":tasks,
             "user":user,
            "project_id":proj.id,
            "project":proj,
            "start_date":tm.start_date,
            "sub_date":tm.end_date,


        }
        # return render(request , 'manager/project/view_project_details.html' , context)
        return render(request , 'task2_app/project_Info.html' , context)
    
@login_required
@role_required('manager')    # managers can navigate to the assign-task form
def view_task_form(request ,proj_id=None):
    proj = get_object_or_404(Project , id=proj_id) if proj_id else None
    print(proj)
    user = request.user
    print("Inside view_task_form :--------> ",user , proj , type(proj))
    
    emp_domains=EmployeeDomain.objects.all()
    tasks = Task2.objects.filter(project=proj)   # must come from task2 model
    teams = Team.objects.filter(manager=user)
    employees = User.objects.filter(role='employee')
    
    print(employees)
    for i in teams:
        print(f"|{i.manager} -> {i.project.title}|")
    
    context={
                "project":proj,
                "employees":employees,
                "tasks":tasks,
                "emp_domains":emp_domains,
                "status":AssignEmployee.STATUS_CHOICES
            }
    return render(request , 'task2_app/assign_task.html',context)


# assign list of tasks 
# managers can assign tasks ,domain,date in  the form
@login_required
@role_required('manager') 
def view_sample(request): 
    if request.method == 'POST':
        try:
            domain_id = request.POST.get("domain")
            proj_id = request.POST.get("proj_id")
            manager_id = request.POST.get("manager_id")
            task_date = request.POST.get("end_date")
            # status = request.POST.get("status")
            task_list = request.POST.getlist("tasks[]")
            print(task_list)
            print(type(task_list))
        except:
            print("aasign task first")
            return JsonResponse({
            'message':"cannot assign employee if u do not assigned task "
           })

        domain=EmployeeDomain.objects.get(id=domain_id)
        print(domain,proj_id,manager_id,task_date)
        user = User.objects.get(id=manager_id)  
        project = Project.objects.get(id=proj_id)
        team=Team.objects.get(project=project,manager=user)
        sub_date= team.end_date
        tk_date = datetime.strptime(task_date, "%Y-%m-%d").date()
        # sb_date = datetime.strptime(str(sub_date), "%Y-%m-%d").date()

        if tk_date >= sub_date:
            return JsonResponse({
            'message':"date must not exeed Submission date "
        })



        Task2.objects.create(
                            tasks=task_list,
                            domain=domain,
                            project=project,
                            manager=user,
                            end_date=task_date
                            )
        return JsonResponse({
            'message':"Task saved successfully"
        })
       
@login_required
@role_required('manager') 
def view_employeeForm(request,proj_id=None):  # managers can navigate to the assign-emp form
    project = get_object_or_404(Project, id=proj_id) if proj_id else None
    status_choices = AssignEmployee.STATUS_CHOICES
    employees=User.objects.filter(role='employee')
    emp=[]
    # _______________________________________
    for e in employees:
        # asg_emp=AssignEmployee.objects.filter(assigned_to=e)   
        # for p in asg_emp:
        ct=AssignEmployee.objects.filter(assigned_to=e).values('project').distinct().count()
        # if ct == 3:
        emp.append({
            'e_id':e.id,
            'ct':ct,
            'fullname':f"{e.first_name} {e.last_name}({e.designation_e}) "
        })
    print(emp)

    

    # _______________________________________
    








    task_row=Task2.objects.filter(project=project)
    print(employees)
    return render(request ,'task2_app/assign_employee.html', {'status_choices':status_choices , 'project':project , 'employees':employees})

@login_required
@role_required('manager') 
def assign_employee(request):
    if request.method == 'POST':
        # domain = request.POST.get("domain")
        proj_id = request.POST.get("proj_id")
        emp_id = request.POST.get("emp_id")
        manager_id = request.POST.get("manager_id")
        status = request.POST.get("status")
        emp = User.objects.get(id=emp_id , role='employee')  
        manager = User.objects.get(id=manager_id)  
        project = Project.objects.get(id=proj_id)
        print("hello")
        # task=Task2.objects.filter(project=project ,manager=manager).first()
        task=Task2.objects.filter(project=project ,manager=manager).order_by('-id').first()
        # if not AssignEmployee.objects.filter(
        #                         task=task,
        #                         assigned_to=emp,
        #                         assigned_by=manager,
        #                         project=project,
                              
        #                     ).count()>3
        AssignEmployee.objects.create(
                                task=task,
                                assigned_to=emp,
                                assigned_by=manager,
                                project=project,
                                status=status
                            )
        return JsonResponse({
            'message':"Employee has been assigned successfully !!"
        })
    
# employee can see the task
@login_required
@role_required('employee')
def my_task(request,proj_id=None):
    project = get_object_or_404(Project , id=proj_id) if proj_id else None
    user = request.user
    userInfo=User.objects.get(id=user.id)
    
    domain=userInfo.designation_e
    print("userInfo -> ",userInfo , "domain -> ",domain)
    # assign_emp = AssignEmployee.objects.get(project=project , assigned_to=userInfo)  # [user:project]
    assign_emp = AssignEmployee.objects.filter(assigned_to=user, project=project).order_by('-id').first()

    print("assign_emp -> ",assign_emp)
    if assign_emp:
        # found the assigned project the user is assigned with
        tk=assign_emp.task # intsance of Task2 model
        print("tk->",tk.id)
        emp_task = Task2.objects.filter(domain=domain).first() # [domain : project]
        tasks_obj = Task2.objects.filter(domain=domain,project=project) # sample
        print("tasks_obj-------------------------------------------->",tasks_obj)
        # --------------------------------------------------------------------------------------------------------
        new_tasks=[]
        new_tasks=[i for t in tasks_obj for i in t.tasks]  # flatten list of tasks
        print(new_tasks)
        
        count=len(new_tasks)*10
        # --------------------------------------------------------------------------------------------------------
        # check how many tasks completed out of total
        no_of_tasks=len(new_tasks)
        prog=Progress.objects.filter(employee=userInfo,project=project)
        complete_tasks=set()
        for p in prog:
            complete_tasks.add(p.task)
            print(f"***{p.id} - {p.task} - {p.status}***********")
        ct=prog.count()
        print(complete_tasks)
        print("===================>>> ",no_of_tasks,ct)
        # --------------------------------------------------------------------------------------------------------
        print("emp_task -> ",emp_task)
        task_list = [i for i in emp_task.tasks]
        print(task_list)
        total=0.0
        is_progress=False
        progress_val=0
        # update = Update.objects.filter(employee=userInfo).order_by('-id').first()
        update = Update.objects.filter(employee=userInfo,project=project).first()

        if update:
            print("update -> ",update,update.total_points)
            total=update.total_points
            progress_val=(total / count)*100
            print(progress_val,count)
            update.percentage=progress_val
            update.save()
            # calculate out ot no.of tasks

            assign_emp.status='In Progress'
            assign_emp.save()
        is_updated=False
        cmplete_task=complete_tasks = list(prog.values_list("task", flat=True))
        print(cmplete_task)
        context={
            'tasks':new_tasks,
            'assign_emp':assign_emp,
            'task_info':emp_task,
            'domain':domain,
            'project':project,
            'total_points':int(total),
            'progress_val':int(progress_val),
            'is_updated':True,
            'prog':prog,
            'complete_tasks':cmplete_task,
            "cmplt_task":ct,
            "total_tasks":no_of_tasks
        }
    return render(request , 'employee2.0/view_assigned_task.html',context)
    
@csrf_exempt
# @require_POST
@login_required
@role_required('employee')
def progress(request):
    user=request.user
    print(user)
    if request.method == 'POST':
        task = request.POST.get('task')
        status = request.POST.get('status')
        employee = request.POST.get('employee')
        domain = request.POST.get('domain')
        project = request.POST.get('project')
        point = float(request.POST.get('point'))
        status='Completed'
        print(task,status,employee,domain,project,point)
       
        domain=EmployeeDomain.objects.get(title=domain)
        project=Project.objects.get(title=project)
        emp=User.objects.get(email=employee)
        # find manager,emp,proj
        # assgn_emp=AssignEmployee.objects.get(project=project , assigned_to=user)
        
        # manager=assgn_emp.assigned_by
        assgn_emp = AssignEmployee.objects.filter(
            project=project,
            assigned_to=user
        ).first()

        if not assgn_emp:
            return JsonResponse({"error": "Assignment not found"}, status=404)

        manager = assgn_emp.assigned_by

        # save to db
        if not Progress.objects.filter(task=task,employee=emp,project=project,domain=domain).exists():
                Progress.objects.create(task=task,
                                        status=status,
                                        point=point,
                                        employee=emp,
                                        project=project,
                                        domain=domain,
                                        is_complete=True
                                    )
        else:
             return JsonResponse({"message":"This task has been already updated" })
        total_points = (Progress.objects.filter(employee=emp,project=project).aggregate(total=Sum('point')))['total'] or 0
        context={'total_points':total_points}
        print(total_points)
        
        # *******************************************************************************************************************
        # no of tasks
        tasks_obj = Task2.objects.filter(domain=domain) # sample
        print("tasks_obj-------------------------------------------->",tasks_obj)
        # --------------------------------------------------------------------------------------------------------
        new_tasks=[]
        new_tasks=[i for t in tasks_obj for i in t.tasks]  # flatten list of tasks
        print(new_tasks)
        count=len(new_tasks)*10
        
        # check if emp exists in Update table then only save it else go for create
        if not Update.objects.filter(employee=emp,project=project).exists():
            percentage_val=(total_points / count)*100
            print(percentage_val,count)
            Update.objects.create(total_points=total_points,employee=emp,project=project,percentage=percentage_val,manager=manager)
        else:
            update=Update.objects.get(employee=emp,project=project)
            update.total_points=total_points
            total=update.total_points
            percentage_val=(total / count)*100
            update.percentage=percentage_val
            print(percentage_val,count)
            update.save()
        # *******************************************************************************************************************
        return JsonResponse({"message":"updated successfully!" , "context":context})

@login_required
@role_required('manager') 
def view_tasks(request,proj_id=None):
    project = get_object_or_404(Project , id=proj_id) if proj_id else None
    user = request.user
    userInfo=User.objects.get(id=user.id , role='manager')
    tasks=Task2.objects.filter(project=project , manager=userInfo)   
    return render(request , 'task2_app/view_tasks.html' , {"tasks":tasks})     

@login_required
@role_required('manager')
def view_employees(request,proj_id=None):
    project = get_object_or_404(Project , id=proj_id) if proj_id else None
    user = request.user
    userInfo=User.objects.get(id=user.id , role='manager')
    return render(request , 'task2_app/view_employees.html') 


@login_required
@role_required('manager')
def view_employees_update(request,proj_id=None):
    project = get_object_or_404(Project , id=proj_id) if proj_id else None
    user = request.user
    userInfo=User.objects.get(id=user.id , role='manager')
    update_list=Update.objects.filter(project=project)
    return render(request , 'task2_app/employee_update.html',{"update_list":update_list}) 

# @login_required
# @role_required('manager')
# def employee_pending_status(request):
#     user=request.user #manager
#     # assgn_emps=AssignEmployee.objects.all()
#     assgn_emps=AssignEmployee.objects.filter(assigned_by=user)
#     print("-------------------------------->>>> ",set(assgn_emps))
#     emps=[]
#     seen=set()
#     for e in assgn_emps:
#         if not Update.objects.filter(employee=e.assigned_to,manager=user).exists():
            
#             # print(d)
#             if e.assigned_to.username not in seen:
#                 seen.add(e.assigned_to.username)
#                 emps.append({
#                 'employee': e.assigned_to,
#                 'Designation': e.assigned_to.designation_e,
#                 'percent': 0
#             })
#     print("------------------->>",emps)
  
#     progress_count=len(emps)
#     return render(request , 'employee2.0/employee_pending.html',{"emp_prog":emps , "progress_count":progress_count})

# @login_required
# @role_required('manager')
# def employee_progress_status(request):
#     user=request.user #manager
#     ups=Update.objects.filter(percentage__lt=100,manager=user)
#     if not ups:
#         return render(request , 'employee2.0/employee_per_status.html',{"progress_count":0})
#     progress_count=ups.count()
#     return render(request , 'employee2.0/employee_per_status.html',{"emp_prog":ups , "progress_count":progress_count})

# @login_required
# @role_required('manager')
# def employee_complete_status(request):
#     user=request.user #manager
#     ups=Update.objects.filter(percentage=100,manager=user)
#     progress_count=ups.count()
#     return render(request , 'employee2.0/employee_per_status.html',{"emp_prog":ups , "progress_count":progress_count})



def _has_project(emp):
    p=[]
    emp=AssignEmployee.objects.filter(assigned_to=emp)
    for i in emp:
        p.append(i.project)
    return set(p)

@login_required
@role_required('manager')
def employee_list(request):
    all_employees = User.objects.filter(role='employee').order_by('date_joined')
    emp_count = all_employees.count()
    # print(all_employees , emp_count) 
    # -----------------------------------------------------------------
    notAssigned=False
    domains=EmployeeDomain.objects.all()
    all_emps=[]
    for i in all_employees:
        if not AssignEmployee.objects.filter(assigned_to=i).exists():
            notAssigned=True
            projects=None
        else:
            projects=_has_project(i)
            # print(projects)

        all_emps.append({
            'full_name':i.first_name+" "+i.last_name,
            'designation':i.designation_e,
            'yoe':i.yop,
            'notAssigned':notAssigned,
            'projects':projects


        })
    print("---------------------------------------------")
    print(all_emps)
    print("---------------------------------------------")
    # -----------------------------------------------------------------
    # pagination
    paginator = Paginator(all_emps , per_page=5 )  # can add  orphans=1 if any extra row remains that will get adjusted in the last page
    page_number = request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    # print("Page number : ",page_number)
    # print("Page obj : ",page_obj)
    if request.method =='POST':
        html_data = render_to_string(
           'employee2.0/partials/employee_row.html',
            {
                "page_obj": page_obj,
          
            }
        )

        return JsonResponse({"data": html_data ,"designation":0,"emp_count":0})

    return render(request , 'employee2.0/all_employees.html' , {"page_obj":page_obj , "domains":domains, "emp_count":emp_count})




@login_required
@role_required('manager')
def domain_category(request):
    if request.method == 'POST':
        domain_id = request.POST.get('domain')

        dm = EmployeeDomain.objects.get(id=domain_id)
        domain=dm.title
        all_employees = User.objects.filter(
            role='employee',
            designation_e=dm
        ).order_by('date_joined')

        emp_count = all_employees.count()
        domains = EmployeeDomain.objects.all()

        all_emps = []

        for emp in all_employees:
            # reset per employee
            notAssigned = False
            projects = None

            if not AssignEmployee.objects.filter(assigned_to=emp).exists():
                notAssigned = True
            else:
                projects = _has_project(emp)

            all_emps.append({
                'full_name': f"{emp.first_name} {emp.last_name}",
                'designation': emp.designation_e,
                'yoe': emp.yop,
                'notAssigned': notAssigned,
                'projects': projects
            })

        paginator = Paginator(all_emps, per_page=5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        html_data = render_to_string(
           'employee2.0/partials/employee_row.html',
            {
                "page_obj": page_obj,
          
            }
        )

        return JsonResponse({"data": html_data ,"designation":domain,"emp_count":emp_count})

# def domain_category(request):
#     if request.method =='POST':
#         domain_id=request.POST.get('domain')
#         print(domain_id , type(domain_id))
#         dm=EmployeeDomain.objects.get(id=int(domain_id))
#         print(dm,dm.id,dm.title)
#         all_employees = User.objects.filter(role='employee',designation_e=dm).order_by('date_joined')
#         print(all_employees)
#         emp_count = all_employees.count()
#         notAssigned=False
#         domains=EmployeeDomain.objects.all()
#         all_emps=[]
#         for i in all_employees:
#             if not AssignEmployee.objects.filter(assigned_to=i).exists():
#                 notAssigned=True
#                 projects=None
#             else:
#                 projects=_has_project(i)
#                 # print(projects)

#             all_emps.append({
#                 'full_name':i.first_name+" "+i.last_name,
#                 'designation':i.designation_e,
#                 'yoe':i.yop,
#                 'notAssigned':notAssigned,
#                 'projects':projects


#             })
#         print("---------------------------------------------")
#         print(all_emps)
#         print("---------------------------------------------")
#         # pagination
#         paginator = Paginator(all_emps , per_page=5 )  # can add  orphans=1 if any extra row remains that will get adjusted in the last page
#         page_number = request.GET.get('page')
#         page_obj= paginator.get_page(page_number)
        
#         html_data=render_to_string('employee2.0/all_employees.html' , {"page_obj":page_obj , "domains":domains, "emp_count":emp_count})
#         # print(html_data)
#         return JsonResponse({"data":html_data})





@login_required
@role_required('manager')
def view_team(request,proj_id=None):
    project=Project.objects.get(pk=proj_id)
    # all_employees = User.objects.filter(role='employee').order_by('date_joined')
    # emp_count = all_employees.count()
    # print(all_employees , emp_count) 

    # # pagination
    # paginator = Paginator(all_employees , per_page=5 )  # can add  orphans=1 if any extra row remains that will get adjusted in the last page
    # page_number = request.GET.get('page')
    # page_obj= paginator.get_page(page_number)
    # print("Page number : ",page_number)
    # print("Page obj : ",page_obj)

    user=request.user
    assgn_emps=AssignEmployee.objects.filter(assigned_by=user,project=project)
    emps=[]
    seen=set()
    for e in assgn_emps:
        # if not Update.objects.filter(employee=e.assigned_to,manager=user).exists():
            
            # print(d)
            if e.assigned_to.username not in seen:
                seen.add(e.assigned_to.username)
                emps.append({
                'employee': e.assigned_to,
                'Designation': e.assigned_to.designation_e,
                'yoe': e.assigned_to.yop
            })
    print("team---------------: ",emps)
    emp_count=len(emps)

    return render(request , 'employee2.0/view_team.html' , {"emps":emps ,  "emp_count":emp_count})


# ------------------------------ chatbot -----------------------------
def _build_timeline_prompt(project_desc, expected_timeline, team):
    return f"""
            You are a SENIOR PROJECT DELIVERY MANAGER with 10+ years of experience in
            Agile and Waterfall planning for software products.

            Your output MUST strictly follow all rules below.
            If any rule is violated, the output is considered INVALID.

            ==================================================================
            PROJECT INPUT
            ==================================================================

            Project Description:
            {project_desc}

            Expected Timeline:
            {expected_timeline}

            Team Details (name, role, experience in years, domain):
            {json.dumps(team, indent=2)}

            ==================================================================
            MANDATORY OUTPUT REQUIREMENTS
            ==================================================================

            You MUST generate EXACTLY TWO timelines for the SAME project and team:

            1) Phase-wise Timeline (Sequential / Waterfall)
            2) Parallel Timeline (Agile / Incremental)

            Output MUST be in HUMAN-READABLE BULLET POINTS ONLY.
            DO NOT return JSON, tables, or paragraphs.

            ==================================================================
            1) PHASE-WISE TIMELINE (STRICT WATERFALL)
            ==================================================================

            Rules (NON-NEGOTIABLE):

            - Phases MUST be strictly sequential (NO overlap)
            - UI/UX MUST be completed before ANY development
            - Backend MUST be completed before Frontend and Mobile start
            - Frontend and Mobile MUST start ONLY after backend completion
            - QA MUST start ONLY after Frontend + Mobile are fully completed
            - Deployment MUST be a SEPARATE final step (not merged with QA)

            Each phase MUST include:
            - Phase Name
            - Duration (in days)
            - Team Members
            - Deliverables

            ==================================================================
            2) PARALLEL TIMELINE (STRICT AGILE / INCREMENTAL)
            ==================================================================

            Rules (NON-NEGOTIABLE):

            - Backend MUST be broken into CLEAR API-LEVEL ACTIVITIES
            (example: Auth API, Event API, Payment API)
            - Each Backend API MUST explicitly state its deliverable
            - Frontend and Mobile activities MUST depend on SPECIFIC APIs
            - As soon as an API is completed, integration MUST begin
            - Frontend/Mobile CANNOT depend on "Backend Development" as a whole
            - QA MUST NOT run in parallel with development
            - QA MUST start ONLY after ALL user-facing features are complete
            - Deployment MUST occur ONLY after successful QA

            Each activity MUST include:
            - Activity Name
            - Duration (in days)
            - Depends On (explicit dependency)
            - Team Members
            - Deliverable

            ==================================================================
            PLANNING CONSTRAINTS (STRICTLY ENFORCED)
            ==================================================================

            - Use ALL team members where applicable
            - More experience = faster delivery
            - Less than 1 year experience = ADD BUFFER explicitly
            - 0-year developers CANNOT work alone on complex tasks
            - Senior developers MUST review junior work
            - Always include QA and Deployment
            - Durations MUST be realistic and in DAYS ONLY

            ==================================================================
            FINAL OUTPUT FORMAT (MANDATORY)
            ==================================================================

            Phase-wise Timeline:
            - Phase 1: ...
            - Duration: X days
            - Team Members: ...
            - Deliverables: ...
            - Phase 2: ...

            Parallel Timeline:
            - Stream 1: Backend APIs
            - Activity 1: ...
                - Duration: X days
                - Depends on: ...
                - Team Members: ...
                - Deliverable: ...
            - Stream 2: Frontend
            - Stream 3: Mobile
            - Stream 4: QA & Deployment

            DO NOT add explanations, summaries, or extra text.
           """

@login_required
@role_required('manager')
def timeline_ai(request):
    user = request.user
    users = User.objects.filter(role='employee')

    if request.method == "POST":
        project_desc = request.POST.get("project_description", "").strip()
        expected_timeline = request.POST.get("expected_timeline", "").strip()

        team_raw = request.POST.get("team")
        try:
            team = json.loads(team_raw)
            print(team)
        except Exception:
            return JsonResponse({"error": "Invalid team data"}, status=400)

        #  LIMIT INPUT SIZE
        project_desc = project_desc[:1800]

        # REDUCE TEAM SIZE
        # team_summary = ", ".join(
        #     f"{m.get('name')}({m.get('role')})" for m in team
        # )

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            
        )

        prompt = _build_timeline_prompt(project_desc, expected_timeline, team)

        response = llm.invoke(prompt)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.replace("```", "").strip()

        return JsonResponse({"timeline": raw})

    return render(request, "chatBot/timeline.html", {"users": users})





# ///////////////////////////////////////////////////////////////////////////////  update



@login_required
@role_required('manager')
def employee_pending_status(request , proj_id=None):
    user=request.user #manager
    # assgn_emps=AssignEmployee.objects.all()
    project=get_object_or_404(Project ,id=proj_id) if proj_id else None
    assgn_emps=AssignEmployee.objects.filter(assigned_by=user , project=project)
    print("-------------------------------->>>> ",set(assgn_emps))
    emps=[]
    seen=set()
    for e in assgn_emps:
        if not Update.objects.filter(employee=e.assigned_to,manager=user).exists():
            
            # print(d)
            if e.assigned_to.username not in seen:
                seen.add(e.assigned_to.username)
                emps.append({
                'employee': e.assigned_to,
                'Designation': e.assigned_to.designation_e,
                'percent': 0
            })
    print("------------------->>",emps)
  
    progress_count=len(emps)
    return render(request , 'employee2.0/employee_pending.html',{"emp_prog":emps , "progress_count":progress_count})


@login_required
@role_required('manager')
def employee_progress_status(request , proj_id=None):
    user=request.user #manager
    project=get_object_or_404(Project ,id=proj_id) if proj_id else None
    ups=Update.objects.filter(percentage__lt=100,manager=user , project=project)
    if not ups:
        return render(request , 'employee2.0/employee_per_status.html',{"progress_count":0})
    progress_count=ups.count()
    return render(request , 'employee2.0/employee_per_status.html',{"emp_prog":ups , "progress_count":progress_count})

@login_required
@role_required('manager')
def employee_complete_status(request,proj_id=None):
    user=request.user #manager
    project=get_object_or_404(Project ,id=proj_id) if proj_id else None
    ups=Update.objects.filter(percentage=100,manager=user,project=project)
    progress_count=ups.count()
    return render(request , 'employee2.0/employee_per_status.html',{"emp_prog":ups , "progress_count":progress_count})