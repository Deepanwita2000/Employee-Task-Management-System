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

from django.utils import timezone
from datetime import timedelta

from team_app.models import Team

from task_app.models import Task
from .authentication import JWTAuthentication, create_access_token, create_refresh_token
from .models import  User, UserToken
from .permissions import IsEmployee,IsEmployeeOrManager
from .serializers import UserSerializer

from account_app.decorators import jwt_required

# _____________________________ for AJAX
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash

from django.contrib.auth.decorators import login_required
from task_app.decorators import role_required
from comment_app.models import Comment
from django.contrib.auth.forms import PasswordChangeForm,AuthenticationForm,SetPasswordForm

# APIView is the base class for all views in Django REST Framework.
# It provides request.data, request.user, request.auth, authentication_classes, permission_classes and methods like .get(), .post()
class RegisterAPIView(APIView):
    permission_classes = [AllowAny] # anyone can access this endpoint
    authentication_classes = []
    # role=None
    # def post(self, request: Request ):
    #     role=self.role
             
    #     # print(f'Request : {request.path}')
    #     # paths=request.path.split("/")
    #     # print(paths[-2])
    #     # if paths[-2] == 'manager':
    #     #     role='manager'
    #     # elif paths[-2] == 'employee':
    #     #     role='employee'
        
    #     # if role not in ('manager' , 'employee'):
    #     #     return Response({"error":"Invalid role"} , status=400)
        
    #     # FIX: make a mutable copy
    #     data = request.data.copy()
    #     data['role'] = role

    #     print("Final data going to serializer:", data)

    #     # print("----------------------------------------------------------------------------------------")
    #     # print("before request.data : ",request.data)
    #     # request.data['role']=role
    #     # print("after request.data : ",request.data)
    #     # user = request.data
    #     # print(f'User data received: {user}')
    #     # print("----------------------------------------------------------------------------------------")

       

    #     # if User.objects.filter(email=user['email']).exists():
    #     #     raise exceptions.APIException('Email already exists!')

    #     # if User.objects.filter(username=user['username']).exists():
    #     #     raise exceptions.APIException('Username already exists!')

    #     # if user['password'] != user['password_confirm']:
    #     #     raise exceptions.APIException('Passwords do not match!')

    #     serializer = UserSerializer(data=data)
        
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     print(serializer.data)
    #     return Response(serializer.data)  
    
    def post(self, request, role):   # <-- URL argument comes here
        data = request.data.copy()

        # Set backend-controlled role
        data['role'] = role        

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
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

############################################################### AJAX ###################################################################
def register_view(request):
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
        return render(request, 'account/register.html', {'roles': User.ROLE_CHOICES , 'user':user_role})

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
            
            designation = request.POST.get("designation", '').strip()
            date_joined = request.POST.get("date", '').strip()

            password = request.POST.get("password", '')
            password_confirm = request.POST.get("password_confirm", '')
            role = request.POST.get("role", '')

            image = request.FILES.get("user_image","")
            bio = request.POST.get("bio", '').strip()

            # Validation
            if not all([first_name, last_name, username, email,designation,date_joined, password, password_confirm ]):
                return JsonResponse({'error': 'All fields are required!'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists!'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists!'}, status=400)

            if password != password_confirm:
                return JsonResponse({'error': 'Passwords do not match!'}, status=400)

            if len(password) < 5:
                return JsonResponse({'error': 'Password must be at least 5 characters long'}, status=400)

            # Create the user (inactive)
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                date_joined=date_joined,
                designation=designation,
                password=password,
                role=role,
                gender=gender,
                yop=yop,
                age=age,
                image = image,
                bio=bio,
                is_active=True  # need to be false later
            )

            print("User created successfully:", user.email)

            # Send verification email
            

            return JsonResponse({
                'success': True,
                'message': 'registration successfull !!!',
                'redirect_url': '/account/sample_login/'
            }, status=200)

        except Exception as e:
            print("Error during registration:", str(e))
            if user:  # Delete only if user was created
                user.delete()
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

def login_view(request):
    if request.method == 'GET':
        return render(request, 'account/login.html')

    elif request.method == 'POST':
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")

            user = authenticate(request, username=email, password=password)
            print(user)
            
            if user is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
            
            # if not user.is_active:
            #     return JsonResponse({'status': 'error','message': 'Your email is not verified. Please check your inbox and activate your account.'}, status=403)

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
    user=request.user
    userInfo = User.objects.get(email=user)
    print(user , user.id)
    print(user)
    if user.role == 'manager':
        title=set()
        all_projects = Team.objects.filter(manager=user)
        count_pending_tasks = Task.objects.filter(assigned_by=user,status='pending').count() 
        count_progress_tasks = Task.objects.filter(assigned_by=user,status='in progress').count() 
        count_complete_tasks = Task.objects.filter(assigned_by=user,status='completed').count() 
        # task=Task.objects.filter(assiged_by=user)
        for i in all_projects:
            title.add(i.project)
        print("My project: ",all_projects)
        print(title)
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
        all_projects = Task.objects.filter(assigned_to=user)
        comments=Comment.objects.filter(commented_to=user)
        
        for i in all_projects:
            title.add(i.project)
        print("My project: ",all_projects)
        print(title)
        context = {
            'user': request.user,
            'username': request.user.username,
            "count" :len(title),
            "com_count":comments.count()
        }
        # html=render_to_string('other/sidenav.html' , context)
        # print(html)

  
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


@login_required
@role_required('manager', 'employee')
def user_profile(request):
    user=request.user
    userInfo = User.objects.get(email=user)
    print(userInfo)
    print(userInfo.image)
    # html=render_to_string('other/sidenav.html' ,{"userInfo":userInfo})
    return render(request , 'account/my_profile.html' ,{"userInfo":userInfo})

#  chnge password with old password
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




#  chnge password without old password
@login_required
@role_required('manager', 'employee')
def user_change_pass1(request):
    user=request.user
    print("user_change_pass1() -> ",user)
    if user.is_authenticated:
        if request.method == 'POST':
            fm= SetPasswordForm(user=request.user , data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request , fm.user)
                messages.success(request, 'Password changed successfully !!' )
                return redirect('user_profile')
        else:
            fm =SetPasswordForm(user=request.user)
        
        return render(request , 'account/changepass1.html',{'form':fm})
    return redirect('login_ui')



#  Forgot Password in login time
# @login_required
# @role_required('manager', 'employee')
def change_password(request):
    user = None
    form = None
    message = ""
    if request.method == 'POST':
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            message = "User not found"
        else:
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("sample_login")
    else:
        form = SetPasswordForm(User())  # empty form for initial display        
    return render(request , 'account/forgot_password.html', {"form": form, "message": message})

    
    # # return redirect('sample_login')
    # user = None
    # form = None
    # message = ""

    # if request.method == "POST":
    #     username = request.POST.get("username")
    #     user = User.objects.filter(username=username).first()

    #     if not user:
    #         message = "User not found"
    #     else:
    #         form = SetPasswordForm(user, request.POST)
    #         if form.is_valid():
    #             form.save()
    #             return redirect("login")
    # else:
    #     form = SetPasswordForm(User())  # empty form for initial display

    # return render(request, "reset_password.html", {"form": form, "message": message})

    
# #___________________________________________________________________________________________________________
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
            
            # if not user.is_active:
            #     return JsonResponse({'status': 'error','message': 'Your email is not verified. Please check your inbox and activate your account.'}, status=403)
            
            
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


def choice_role(request):
    return render(request ,'sample_account/choice_role.html' )

def sample_register(request):
    # if request.method == 'GET':
    #     user = request.user
    #     print("path : ",request.path)
    #     paths=request.path.split("/")
    #     print(paths)
    #     if paths[len(paths)-2] == 'register_manager':
    #         user_role='manager'
    #     if paths[len(paths)-2] == 'register_employee':
    #         user_role='employee'
    #     print(user_role)
    #     return render(request,'sample_account/register.html', {'roles': User.ROLE_CHOICES , 'user':user_role})
    return render(request,'sample_account/register.html')