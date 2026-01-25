from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from EmployeeTask import settings,views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="EmployeeApp Backend APIs",
      default_version='v1',
      description="This is the API documentation for EmployeeApp project APIs",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="deepanwita448@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('' , views.home , name='home'),
    path('account/' , include("account_app.urls")),
   #  path('task/' , include("task_app.urls")),
   #  path('comment/' , include("comment_app.urls")),

   #  ////////////////////////////////////// new added features //////////////////
    path('task2/' , include("task2_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)