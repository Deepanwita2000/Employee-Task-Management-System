from django.shortcuts import redirect, render,get_object_or_404
from django.template.loader import render_to_string
# Create your views here.
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode

import random
# from django.utils import timezone
from datetime import datetime, timedelta
# from datetime import datetime, timedelta, timezone
from team_app.models import Team

# from task_app.models import Task
from .authentication import JWTAuthentication, create_access_token, create_refresh_token
from .models import  User, UserToken,OTP,ManagerDomain,EmployeeDomain
  
from .permissions import IsEmployee,IsEmployeeOrManager
from .serializers import UserSerializer

from account_app.decorators import jwt_required
# _______________________________________________________________ for AJAX
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash

from django.contrib.auth.decorators import login_required

from task2_app.decorators import role_required

from django.contrib.auth.forms import PasswordChangeForm,AuthenticationForm,SetPasswordForm

from task2_app.models import AssignEmployee,Task2, Update
from django.utils import timezone
from datetime import timedelta  
user_list=[]


        



# User Login with JWT
class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # Anyone can login
    authentication_classes = []  # No authentication required for login

    def post(self, request: Request):
        email = request.data['email']
        password = request.data['password']        

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if user is None:  
            raise exceptions.AuthenticationFailed('Invalid credentials')
        
        # Check if password is correct
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid password')
        
        info= User.objects.get(email=email)
        print(f"getuser -> {info.is_active}")
        if info.is_active == False:
            return Response(
                {"message":"User has not been activated !!"},status=401
            )
        
        # Generate access and refresh tokens
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        # Save refresh token of a specific user with an expiration date of 7 days
        UserToken.objects.create(
            user=user, 
            token=refresh_token, 
            expired_at = timezone.now() + timedelta(days=7)
        )
        
        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response
    
# Check Authenticated User      
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmployeeOrManager]  # Ensure only authenticated users who can be a professors or students can access this view

    def get(self, request: Request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'role': user.role,
            'is_manager': user.role == 'manager',
            'is_employee': user.role == 'employee',
            'is_admin': user.role == 'admin'            
        })

# Logout User    
class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def post(self, request: Request):
        print(request.data)
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token missing'}, status=400)

        UserToken.objects.filter(token=refresh_token).delete()

        response: Response = Response({
            'status': 'success',
            'message': 'Logged out successfully'
        }, status=200)

        response.delete_cookie(key='refresh_token')
        return response







# ///////////////// redo api/////////////////////
    
class RegisterManagerView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user = request.data
        print(f'User data received: {user}')
        email=user['email']
        print(email)
        if User.objects.filter(email=user['email']).exists():
            raise exceptions.APIException('Email already exists!')

        if User.objects.filter(username=user['username']).exists():
            raise exceptions.APIException('Username already exists!')

        if user['password'] != user['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        user_instance=serializer.save(role='manager')  # role = manager will be saved automatically

        mail_subject = 'Please activate your account'
        email_template = 'account/email/account_verification_email.html'
        send_verification_email(request, user_instance, mail_subject, email_template)
        print("Verification email sent to:", email)
        return Response(
             {
                'success': True,
                'message': 'Check your email for the activation link!',
                'user': serializer.data
            },
            status=201
        )
    
    

        
        
class RegisterEmployeeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user = request.data
        print(f'User data received: {user}')
        email=user['email']
        print(email)
        if User.objects.filter(email=user['email']).exists():
            raise exceptions.APIException('Email already exists!')

        if User.objects.filter(username=user['username']).exists():
            raise exceptions.APIException('Username already exists!')

        if user['password'] != user['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        user_instance=serializer.save(role='employee')  # role = employee will be saved automatically

        mail_subject = 'Please activate your account'
        email_template = 'account/email/account_verification_email.html'
        send_verification_email(request, user_instance, mail_subject, email_template)
        print("Verification email sent to:", email)
        return Response(
             {
                'success': True,
                'message': 'Check your email for the activation link!',
                'user': serializer.data
            },
            status=201
        )



def generate_otp_api():
    code = str(random.randint(100000,999999))
    expires_at= timezone.now() + timedelta(seconds=60)
    return code,expires_at

class ChangePasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self,request):
        user=request.data
        # email,new_pass,confirm_pass
        email=user['email']
        new_pass = user['new_password']
        confirm_pass = user['confirm_password']
        # save password
        userInfo=User.objects.get(email=email)
        # print(f"old password -> {userInfo.password}")
        userInfo.set_password(new_pass)
        userInfo.save()

        mail_subject = 'Please activate your account'
        email_template = 'account/email/send_otp.html'
        # otp=generate_otp_api()
        # print(f"otp is {otp} and user is {email}")
        # OTP.objects.create(otp=otp , user=userInfo)

        otp,expires_at=generate_otp_api()
        print(f"otp is {otp}")
        OTP.objects.create(otp=otp , user=userInfo , expires_at=expires_at)
        user_list.append(user)
        print("from api otp of users: ",user_list)
        send_otp_email(request, userInfo, mail_subject, email_template,otp)
        print("otp sent to:", email)

        return Response({
            'success': True,
            'message': 'Check your email for the activation link!',
            'redirect_url': '/account/add_otp/'
        }, status=200)


############################################################### AJAX ###################################################################

# Activate the user by setting the is_active status to True
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('/account/sample_login/?activated=true')
    else:
        return redirect('/account/sample_login/?invalid_token=true')

# Send verification email
def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)            # Get the current site
   
    message = render_to_string(email_template, {        # Render the email template with the context
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),     # Encode the user's primary key
        'token': default_token_generator.make_token(user),      # Generate a token for the user
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()



def register_view(request):
    mg=None
    emp=None
    if request.method == 'GET':
        user = request.user
        print("path : ",request.path)
        paths=request.path.split("/")
        print(paths)
        if paths[len(paths)-2] == 'register_manager':
            user_role='manager'
        if paths[len(paths)-2] == 'register_employee':
            user_role='employee'
        print(user_role)
        domain_m = ManagerDomain.objects.all()
        domain_e = EmployeeDomain.objects.all()
        return render(request, 'account/register.html', {'roles': User.ROLE_CHOICES , 'manager_domain':domain_m,'emp_domain':domain_e ,'user':user_role})

    elif request.method == 'POST':
        print("POST DATA:", request.POST)
        user = None  # Safeguard for cleanup on exception

        try:
            first_name = request.POST.get("first_name", '').strip()
            last_name = request.POST.get("last_name", '').strip()
            username = request.POST.get("username", '').strip()
            email = request.POST.get("email", '').strip()
            yop = float(request.POST.get("yop", '').strip())
            gender = request.POST.get("gender", '').strip()
            age = int(request.POST.get("age", '').strip())
            
            designation_emp = (request.POST.get("designation_emp", '').strip())
            designation_mg = (request.POST.get("designation_mg", '').strip())
            date_joined = request.POST.get("date", '').strip()

            password = request.POST.get("password", '')
            password_confirm = request.POST.get("password_confirm", '')
            role = request.POST.get("role", '')

            image = request.FILES.get("user_image","")
            bio = request.POST.get("bio", '').strip()
            print("==================================  ",designation_emp,designation_mg)
            print("==================================  ",type(designation_emp),type(designation_mg))
            # Validation
            if not all([first_name, last_name, username, email,date_joined, password, password_confirm ]):
                return JsonResponse({'error': 'All fields are required!'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists!'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists!'}, status=400)

            if password != password_confirm:
                return JsonResponse({'error': 'Passwords do not match!'}, status=400)

            if len(password) < 5:
                return JsonResponse({'error': 'Password must be at least 5 characters long'}, status=400)
            
            if designation_mg:
                mg = ManagerDomain.objects.get(id=int(designation_mg))
            if designation_emp:
                emp=EmployeeDomain.objects.get(id=int(designation_emp))

            # Create the user (inactive)
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                date_joined=date_joined,
                designation_m=mg,
                designation_e=emp,
                password=password,
                role=role,
                gender=gender,
                yop=yop,
                age=age,
                image = image,
                bio=bio,
                is_active=False  # need to be false later
            )

            print("User created successfully:", user.email)

            # Send verification email
             # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'account/email/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            print("Verification email sent to:", email)

            return JsonResponse({
                'success': True,
                'message': 'Check your email for the activation link!',
                'redirect_url': '/account/sample_login/'
            }, status=200)

        except Exception as e:
            print("Error during registration:", str(e))
            if user:  # Delete only if user was created
                user.delete()
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

def sample_login(request):
    if request.method == 'GET':
         return render(request,'sample_account/login.html')
    elif request.method == 'POST':
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            user = authenticate(request, username=email, password=password)
            print(user)
            if not User.objects.filter(email=email).exists():
                print("not exists")
                return JsonResponse({'error': 'Not a registered email'} , status=400)
            
            if user is None:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                # return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
            
            if not user.is_active:
                return JsonResponse({'status': 'error','message': 'Your email is not verified. Please check your inbox and activate your account.'}, status=403)
                   
            login(request, user)
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)

            # Determine redirect URL based on role
            
            if user.role == 'manager':
                redirect_url = '/account/dashboard/'  # or '/program/list/' if needed
            elif user.role == 'employee':
                redirect_url = '/account/dashboard/'
            else:
                redirect_url = '/'  # Fallback or 403 page

            # Save refresh token in DB
            UserToken.objects.create(
                user=user,
                token=refresh_token,
                expired_at=timezone.now() + timedelta(days=7)
            )
            response = JsonResponse({
                "status": "success",
                "redirect_url": redirect_url
            })

            # Set tokens in HTTP-only cookies (for frontend)
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',         # or 'Strict'
                max_age=2400, # Access token  expires in 40 minutes
                path='/'
            )

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,  # 7 days
                path="/"
            )

            return response

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

@jwt_required
def dashboard_view(request):
    ct=0
    user=request.user
    userInfo = User.objects.get(email=user)
    print(user , user.id)
    print(user)
    if user.role == 'manager':
        title=set()
        all_projects = Team.objects.filter(manager=userInfo)
        print("------------------------------>>> ",all_projects)

        count_pending_tasks,count_complete_tasks,count_progress_tasks=0,0,0
        if all_projects:
            assgn_emps=AssignEmployee.objects.filter(assigned_by=userInfo)
                       
            # ----------------------pending
            seen=set()
            for e in assgn_emps:
                if not Update.objects.filter(employee=e.assigned_to,manager=user).exists():
                    if e.assigned_to.username not in seen:
                        seen.add(e.assigned_to.username)
                        
            print(seen)
            count_pending_tasks=len(seen)
            # ----------------------progress
            progress=set()
            for e in assgn_emps:
                if  Update.objects.filter(employee=e.assigned_to,manager=user,percentage__lt=100).exists():
                    print(e.assigned_to.username)
                    if e.assigned_to.username not in progress:
                        progress.add(e.assigned_to.username)
            print("progress --> ",progress)
            count_progress_tasks=len(progress)
            # ----------------------complete
            cmplte=set()
            for e in assgn_emps:
                if Update.objects.filter(employee=e.assigned_to,manager=user,percentage=100).exists():
                    if e.assigned_to.username not in cmplte:
                        cmplte.add(e.assigned_to.username)
            print("cmplte --> ",cmplte)
            count_complete_tasks=len(cmplte) 
            # --------------------------------------------------------
            for i in all_projects:
                title.add(i.project)
            # print("My project: ",all_projects)
            # print(title)
        context = {
            'user': request.user,
            'username': request.user.username,
            "count" :len(title),
            "count_pending_tasks":count_pending_tasks,
            "count_progress_tasks":count_progress_tasks,
            "count_complete_tasks":count_complete_tasks,
        }
        # html=render_to_string('other/sidenav.html' , {"userInfo":userInfo})
        # print(html)
    elif user.role == 'employee':
        title=set()
        # all_projects = Task.objects.filter(assigned_to=user)
        all_projects = AssignEmployee.objects.filter(assigned_to=user)
        # comments=Comment.objects.filter(commented_to=user)
        
        for i in all_projects:
            title.add(i.project)
        print("My project: ",all_projects)
        print(title)
        context = {
            'user': request.user,
            'username': request.user.username,
            "count" :len(title),
            # "com_count":comments.count()
            "com_count":0
        }
       
  
    print(context)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX request, return partial dashboard content only
        return render(request, 'account/dashboard.html', context)
    else:
        # When AJAX request is not detected, render 
        return render(request, 'account/dashboard.html', context)
    
def logout_view(request):
    try:
        user = request.user
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            UserToken.objects.filter(user=user, token=refresh_token).delete()

        logout(request)

       
        response = redirect('sample_login')

        # Delete cookies with the correct paths
        response.delete_cookie('access_token', path='/')     # Access token
        response.delete_cookie('refresh_token', path='/')    # Refresh token

        return response

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ///////////////////////////////////////////////// other features password,change password../////////////////////////////
@login_required
@role_required('manager', 'employee')
def user_profile(request):
    user=request.user
    userInfo = User.objects.get(email=user)
    print(userInfo)
    print(userInfo.image)
    # html=render_to_string('other/sidenav.html' ,{"userInfo":userInfo})
    return render(request , 'account/my_profile.html' ,{"userInfo":userInfo})

# change password with old password inside profile page
@login_required
@role_required('manager', 'employee')
def user_change_pass(request):
    user=request.user
    if user.is_authenticated:

        if request.method == 'POST':
            fm= PasswordChangeForm(user=request.user , data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request , fm.user)
                messages.success(request, 'Password changed successfully !!' )
                return redirect('user_profile')
        else:
            fm =PasswordChangeForm(user=request.user)
        
        return render(request , 'account/changepass.html',{'form':fm})
    return redirect('login_ui')

  
def choice_role(request):
    return render(request ,'sample_account/choice_role.html' )

# /////////////////////////////////  forget password with login

def activate_otp(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('/account/add_otp/?activated=true')
    else:
        return redirect('/account/add_otp/?invalid_token=true')


# Send otp email
def send_otp_email(request, user, mail_subject, email_template,otp_code):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)            # Get the current site
    
    message = render_to_string(email_template, {        # Render the email template with the context
        'user': user,
        'domain': current_site,
        'code':otp_code,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),     # Encode the user's primary key
        'token': default_token_generator.make_token(user),      # Generate a token for the user
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()

# add & verify otp
def add_otp(request):
    if request.method == 'GET':
         return render(request,'account/otpForm.html')
    elif request.method == 'POST':
        otp = request.POST.get('otp')
        print(f"from add otp : ", otp)
        # return redirect('sample_login')
        latest_otp = OTP.objects.latest('created_at')
        if otp != latest_otp.otp:
            print("wrong otp!!")
            return JsonResponse({
                "status": "error",
                "message": 'wrong otp!!'
            })
        
        if timezone.now() > latest_otp.expires_at:
            print("expired otp!!")
            latest_otp.delete()
            
            return JsonResponse({
                "status": "error",
                "message": 'OTP expired!!'
            })
        print("otp matched & now clear it from db")  
        # latest_otp.delete() # remove otp from db after it matches with the real otp.
        return JsonResponse({
                "status": "success",
                "redirect_url": '/account/sample_login/'
            })
       
          
def generate_otp():
    code = str(random.randint(100000,999999))
    expires_at= timezone.now() + timedelta(seconds=60)
    return code,expires_at

def resend_otp(request):
    if request.method == 'POST':
            # latest = OTP.objects.latest('created_at')
            # # latest = OTP.objects.filter(user=request.user).order_by('-created_at').first()

            # if not latest:
            #     return JsonResponse({
            #         "error": "OTP not found. Please generate OTP first."
            #     }, status=400)
            # user=latest.user
            print("resend : ",user_list)
            email=user_list[-1]
            # email = latest.user
            user = User.objects.filter(email=email).first()
            mail_subject = 'Please Verify OTP'
            email_template = 'account/email/send_otp.html'
            otp,expires_at=generate_otp()
            print(f"otp is {otp} sent to {user}")
            OTP.objects.create(otp=otp , user=user , expires_at=expires_at)
            send_otp_email(request, user, mail_subject, email_template,otp)
            print("otp sent to:", email)

           
            message = f"otp sent to your {email}!"

            return JsonResponse({"success":message})

# new forgot password at login time
def change_password(request):
    user = None
    form = None
    message = ""
    if request.method == 'POST':
        try:
            email = request.POST.get("email")
            print(email)
            user = User.objects.filter(email=email).first()
            print(user)
            if not user:
                message = "User not found"
            else:
                form = SetPasswordForm(user, request.POST)
                print("form -------------")
                print(form)
                print("----------------")
                # This password is too short. It must contain at least 8 characters.
                # The password is too similar to the username.
                # This password is too common.
                # This password is entirely numeric.

                #  send otp email
                if form.is_valid():
                    form.save()
                    # return redirect("sample_login")
                    # Send verification email
                    mail_subject = 'Please Verify OTP'
                    email_template = 'account/email/send_otp.html'
                    otp,expires_at=generate_otp()
                    print(f"otp is {otp}")
                    OTP.objects.create(otp=otp , user=user , expires_at=expires_at)
                    user_list.append(user)
                    print(user_list)
                    send_otp_email(request, user, mail_subject, email_template,otp)
                    
                    print("otp sent to:", email)

                    # return JsonResponse({
                    #     'success': True,
                    #     'message': 'Check your email for the activation link!',
                    #     'redirect_url': '/account/add_otp/'
                    # }, status=200)
                    message = "OTP sent to your registered email!"

                else:
                    # show password validation errors under button
                    message = " ".join(
                        err for errors in form.errors.values() for err in errors
                    )

                    
        except Exception as e:
            print("Error during registration:", str(e))
            if user:  # Delete only if user was created
                user.delete()
            return JsonResponse({'error': str(e)}, status=400)
            
    
    else:
        form = SetPasswordForm(User())  # empty form for initial display        
    return render(request , 'account/forgot_password.html', {"form": form, "message": message})



