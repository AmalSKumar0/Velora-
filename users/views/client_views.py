from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from commissions.models import *
from core.models import Tag
from users.decorators import role_required


@login_required
@role_required('client')
def client_dash(request):
    return render(request,'client/dashboard.html')
    
