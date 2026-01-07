from django.urls import include, path

from .views import (view_projects ,view_project_info,view_task_form,view_sample,view_employeeForm,assign_employee,my_task,progress,timeline_ai,view_tasks,view_employees,view_employees_update,
                    employee_progress_status,employee_complete_status,employee_pending_status,employee_list,view_team)
from .views import TeamView,TaskView

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('router',TeamView)
router.register('taskApi',TaskView)


urlpatterns = [
    path('team/',include(router.urls)),
    path('task/',include(router.urls)),


    path('list_projects/',view_projects , name='list_projects'),
    path('project_Info/<int:proj_id>/',view_project_info , name='project_Info'),
    # path('assign_task/',view_task_form , name='assign_task'),
    path('assign_task/<int:proj_id>/',view_task_form , name='assign_task'),
    path('view_sample/',view_sample , name='view_sample'),
    path('view_tasks/<int:proj_id>/',view_tasks , name='view_tasks'),
    path('view_team/<int:proj_id>/',view_team , name='view_team'),
    path('view_employeeForm/<int:proj_id>/',view_employeeForm , name='view_employeeForm'),
    path('assign_employee/',assign_employee , name='assign_employee'),
    path('view_employees/',view_employees , name='view_employees'),
    path('view_employees_update/<int:proj_id>/',view_employees_update , name='view_employees_update'),
    path('my_task/<int:proj_id>/',my_task , name='my_task'),
    path('progress/',progress , name='progress'),
    path('employee_progress_status/',employee_progress_status , name='employee_progress_status'),
    path('employee_complete_status/',employee_complete_status , name='employee_complete_status'),
    path('employee_pending_status/',employee_pending_status , name='employee_pending_status'),
    path('all_employees/',employee_list , name='employee_list'),
    path("timeline_ai/", timeline_ai, name="timeline_bot"),
 ]