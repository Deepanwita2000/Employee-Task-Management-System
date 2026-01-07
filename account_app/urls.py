from django.urls import include, path
from .views import LoginAPIView, LogoutAPIView,  UserAPIView , register_view,dashboard_view,logout_view,user_profile,sample_login,choice_role,change_password,user_change_pass,activate,activate_otp,add_otp,RegisterManagerView,RegisterEmployeeView,ChangePasswordView,resend_otp


urlpatterns = [
    path('register/manager/', RegisterManagerView.as_view()), # role = manager
    path('register/employee/', RegisterEmployeeView.as_view()), # role = employee
    path('login/', LoginAPIView.as_view()),
    path('user/', UserAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('change_pass/', ChangePasswordView.as_view()),

    ############### AJAX 
    
    path('register_employee/', register_view, name='registerEmployee'),
    path('register_manager/', register_view, name='registerManager'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('sample_login/', sample_login, name='sample_login'),  
    # path('sent_otp/<int:otp_code>/', sent_otp, name='sent_otp'),  
    # path('verify_otp/', verify_otp, name='verify_otp'),  
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout_ui/', logout_view, name='logoutUser'),  
    path('activate_otp/<uidb64>/<token>/', activate_otp, name='activate_otp'),   
    path('add_otp/', add_otp, name='add_otp'),   
    path('resend_otp/', resend_otp, name='resend_otp'),   

    path('user_profile/', user_profile, name='user_profile'),  
    path('changepass/', user_change_pass, name='changepass'),  # if user wants to change password inside profile page
    # path('change_pass/', user_change_pass1, name='change_pass'),  # if user wants to change password inside profile page
    path('forgot_password/', change_password, name='forgot_password'),  # during login time
    
    path('choice_role/', choice_role, name='choice_role'),  
    # path('sample_register_employee/', sample_register, name='sample_registerEmployee'),  
    # path('sample_register_manager/', sample_register, name='sample_registerManager'),  


  
                        

]