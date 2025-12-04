from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from EmployeeTask import settings,views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , views.home , name='home'),
    path('account/' , include("account_app.urls")),
    path('task/' , include("task_app.urls")),
    path('comment/' , include("comment_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)