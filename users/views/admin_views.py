from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from commissions.models import *
from core.models import Tag
from users.decorators import role_required
from payments.models import Payment
from django.db.models import Sum, Count, Avg
import json

# admin
@login_required
@role_required('admin')
def admin_dash(request):

    return render(request,'admin/dashboard.html')


@login_required
@role_required('admin')
def users_view(request):
    role_filter = request.GET.get('role')

    users = User.objects.select_related('artist_profile').prefetch_related(
        'artist_profile__tags',
        'artist_profile__portfolio__tags'
    )

    if role_filter:
        users = users.filter(role=role_filter)

    return render(request, 'admin/users/view_users.html', {
        'users': users,
        'selected_role': role_filter
    })

@login_required
@role_required('admin')
def delete_user_view(request,id):
    user = get_object_or_404(User,id=id)
    user.delete()
    return redirect('allusers')

