from django.shortcuts import render,redirect

def home(request):
    return redirect('sample_login')
    # return render(request , 'base.html')