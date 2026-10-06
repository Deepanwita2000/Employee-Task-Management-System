from django.shortcuts import render,redirect

def home(request):
    return redirect('sample_login')
    # return render(request , 'base.html')



import os
from django.contrib.auth import get_user_model
from django.http import JsonResponse


def create_admin(request):
    User = get_user_model()

    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        return JsonResponse(
            {"error": "Admin credentials are not configured."},
            status=500
        )

    if User.objects.filter(email=email).exists():
        return JsonResponse({"message": "Admin already exists."})

    User.objects.create_superuser(
        username="admin",
        email=email,
        password=password,
        first_name="Admin",
        last_name="User",
        role=User.MANAGER,
        gender="Other",
    )

    return JsonResponse({"message": "Superuser created successfully."})