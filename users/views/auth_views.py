from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from commissions.models import *
from core.models import Tag
from users.decorators import role_required

def home(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, 'home.html')

    if user.is_superuser:
        return redirect('adminDashboard')

    if user.role == "client":
        return redirect("clientDashboard")

    elif user.role == "artist":
        return redirect("artistDashboard")

    return render(request, 'home.html')


User = get_user_model()


def login_view(request):
    next_url = request.GET.get('next')
    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request,'Insert valid data')
            return render('login')


        if not User.objects.filter(email=email).exists():
            messages.error(request,'Invalid credentials')
            return redirect('login')

        userobj = User.objects.get(email=email)
        username = userobj.username
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request,'Invalid credentials')
            return redirect('login')

        login(request,user)
        if next_url:
            return redirect(next_url)

        if user.is_superuser:
            return redirect("adminDashboard")

        if user.role == "client":
            return redirect("clientDashboard")

        elif user.role == "artist":
            return redirect("artistDashboard")
        
        else:
            messages.error(request,'invalid user')
            return render('login')


    return render(request,'auth/login.html')


def register_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")


        if not username or not email or not password or not role:
            messages.error(request, "All fields are required")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
            return redirect("register")


        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        login(request,user)

        if user.role == "client":
            return redirect("clientDashboard")

        elif user.role == "artist":
            return redirect("create_artist_profile")
        
        else:
            messages.error(request,'invalid user')
            return render('login')

    return render(request, "auth/signup.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")

