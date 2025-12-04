from django.urls import include, path
from .views import LoginAPIView, LogoutAPIView, RegisterAPIView, UserAPIView , register_view,login_view,dashboard_view,logout_view,user_profile,sample_login,choice_role,sample_register,user_change_pass1,change_password



urlpatterns = [
    path('register/manager/', RegisterAPIView.as_view(), {'role': 'manager'}),
    path('register/employee/', RegisterAPIView.as_view(), {'role': 'employee'}),
    path('login/', LoginAPIView.as_view()),
    path('user/', UserAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),

    ############### AJAX
    # path('register_ui/', register_view, name='registerUser'),
    path('register_employee/', register_view, name='registerEmployee'),
    path('register_manager/', register_view, name='registerManager'),
   
    path('login_ui/', login_view, name='loginUser'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout_ui/', logout_view, name='logoutUser'),  
    path('user_profile/', user_profile, name='user_profile'),  
    # path('changepass/', user_change_pass, name='changepass'),  
    path('change_pass/', user_change_pass1, name='change_pass'),  
    path('forgot_password/', change_password, name='forgot_password'),  




    path('sample_login/', sample_login, name='sample_login'),  
    path('choice_role/', choice_role, name='choice_role'),  
    path('sample_register_employee/', sample_register, name='sample_registerEmployee'),  
    path('sample_register_manager/', sample_register, name='sample_registerManager'),  


  
                        

]