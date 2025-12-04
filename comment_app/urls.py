from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('create/<int:pk>/' , views.create_comment , name='comments'),
    path('view_messages/' , views.view_messages , name='view_messages'),
    # path('create_comment_pro/' , views.create_comment_pro , name='comments_pro'),

]
