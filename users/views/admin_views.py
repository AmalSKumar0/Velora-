from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from django.core.paginator import Paginator
from commissions.models import *
from core.models import Tag
from users.decorators import role_required
from payments.models import Payment
from django.db.models import Sum, Count, Avg,F
import json
from django.db.models.functions import TruncMonth
from datetime import timedelta
from django.utils import timezone


# admin
@login_required
@role_required('admin')
def admin_dash(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    six_months_ago = now - timedelta(days=180)

    total_users = User.objects.count()
    new_users_month = User.objects.filter(created_at__gte=thirty_days_ago).count()

    revenue_agg = Payment.objects.filter(status=Payment.Status.RELEASED).aggregate(total=Sum('amount'))
    total_revenue = revenue_agg['total'] or 0
    
    active_orders = Order.objects.filter(status=Order.Status.IN_PROGRESS).count()
    pending_orders = Order.objects.filter(status=Order.Status.SUBMITTED).count()

    completed_orders = Order.objects.filter(status=Order.Status.COMPLETED)
    avg_delivery_days = 0
    if completed_orders.exists():
        avg_time = completed_orders.aggregate(
            avg=Avg(F('updated_at') - F('created_at'))
        )['avg']
        if avg_time:
            avg_delivery_days = round(avg_time.total_seconds() / 86400, 1)

    monthly_revenue = Payment.objects.filter(
        status=Payment.Status.RELEASED,
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')) \
     .values('month') \
     .annotate(total=Sum('amount')) \
     .order_by('month')

    revenue_labels = []
    revenue_data = []
    for i in range(5, -1, -1):
        target_month = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        revenue_labels.append(target_month.strftime('%b'))
        
        val = next((item['total'] for item in monthly_revenue if item['month'].month == target_month.month), 0)
        revenue_data.append(val)

    top_tags = Tag.objects.filter(requests__order__isnull=False) \
        .annotate(order_count=Count('requests__order')) \
        .order_by('-order_count')[:4]

    category_labels = [tag.name for tag in top_tags]
    category_data = [tag.order_count for tag in top_tags]
    
    colors = ['#ffc86b', '#ff90eb', '#7ae582', '#f3f4f6']
    top_categories_legend = [
        {'name': tag.name, 'color': colors[i % len(colors)]} 
        for i, tag in enumerate(top_tags)
    ]

    context = {
        'total_users': total_users,
        'new_users_month': new_users_month,
        'total_revenue': total_revenue,
        'active_orders': active_orders,
        'pending_orders': pending_orders,
        'avg_delivery_days': avg_delivery_days,
        
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        
        'top_categories_legend': top_categories_legend,
    }

    return render(request, 'admin/dashboard.html', context)


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

@login_required
@role_required('admin')
def admin_requests(request):
    requests_list = Request.objects.select_related('client').prefetch_related('tags').order_by('-created_at')
    paginator = Paginator(requests_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'requests': page_obj, 
    }
    return render(request, 'admin/requests.html', context)