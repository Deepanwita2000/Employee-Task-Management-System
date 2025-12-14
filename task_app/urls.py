from django.urls import include, path
from .views import (TaskViewSet,serach_by_employee_id,create_task,get_task_rows,program_list,update_status,get_task_rows_employee,
                    edit_task,delete_task,emp_task_list,all_employees_completed,best_employees,
                    view_projects,view_project_details,add_task,view_task_form,view_team_members,view_alloted_task,analyze_progress,view_progress,employee_line_graph,
                    employee_list,employeeList_pending_status,employeeList_progress_status,employeeList_complete_status,chatBot,
                    myTodo)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tasks', TaskViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('search_task/<int:pk>/', serach_by_employee_id , name='serach_by_employee_id'),
    
    # path('get_task_rows/', get_task_rows , name='get_task_rows'),
    # path('get_task_rows_employee/', get_task_rows_employee , name='get_task_rows'),
    # path('program_list/', program_list , name='program_list'),
    # path('emp_task_list/', emp_task_list , name='emp_task_list'),


    path('create_task/', create_task , name='create_task'),
    path('edit_task/<int:task_id>/', edit_task , name='edit_task'),
    path('delete_task/<int:task_id>/', delete_task , name='delete_task'),

    
    # # path('get_task_rows/', get_task_rows , name='get_task_rows'),
    # path('all_employees_completed/', all_employees_completed , name='all_employees_completed'),
    # path('best_employees/', best_employees , name='best_employees'),


#///////////////////////////////// Renew /////////////////////////////////
    path('view_task_form/<int:proj_id>/',view_task_form , name='view_task_form'),
    path('add_task/',add_task , name='add_task'),
    path('view_projects/',view_projects , name='view_projects'),
    path('view_project_details/<int:proj_id>/',view_project_details , name='view_project_details'),
    path('employee_line_graph/<int:employee_id>/', employee_line_graph, name='employee_line_graph'),
    path('employee_list/', employee_list, name='employee_list'),
    # path('employee_list_check_box/', employee_list_check_box, name='employee_list_check_box'),
    path('employeeList_pending_status/', employeeList_pending_status, name='employeeList_pending_status'),
    path('employeeList_progress_status/', employeeList_progress_status, name='employeeList_progress_status'),
    path('employeeList_complete_status/', employeeList_complete_status, name='employeeList_complete_status'),


    
   
# ------- for employees ---------------
   path('view_team_members/<int:proj_id>/',view_team_members , name='view_team_members'),
   path('view_alloted_task/',view_alloted_task , name='view_alloted_task'),
   path('update_status/<int:id>/<str:status>/', update_status, name='update_status'),
   path('analyze_progress/', analyze_progress, name='analyze_progress'),
   path('view_progress/<int:user_id>/', view_progress, name='view_progress'),
   path('myTodo/', myTodo, name='myTodo'),
   path('chatBot/', chatBot, name='chatBot'),

]