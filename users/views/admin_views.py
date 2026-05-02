import tempfile
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
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from payments.services.payment_service import PaymentService

def download_admin_report(request):
    # 1. Gather Data from Database
    now = timezone.now()
    
    data = {
        'generated_at': now,
        'total_revenue': Payment.objects.filter(status='released').aggregate(Sum('amount'))['amount__sum'] or 0,
        'escrow_funds': Payment.objects.filter(status='held').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_users': User.objects.count(),
        'total_orders': Order.objects.count(),
        'completion_rate': 0,
        'recent_orders': Order.objects.select_related('client', 'artist').order_by('-created_at')[:10],
        'top_tags': Tag.objects.annotate(num_req=Count('requests')).order_by('-num_req')[:5],
    }

    total_orders = data['total_orders']
    if total_orders > 0:
        completed = Order.objects.filter(status='completed').count()
        data['completion_rate'] = round((completed / total_orders) * 100, 1)

    html_string = render_to_string('admin/reports/pdf_template.html', data)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = f'attachment; filename=Velora_Global_Report_{now.strftime("%Y%m%d")}.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response


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

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/users/view_users.html', {
        'users': page_obj,
        'selected_role': role_filter
    })

from django.views.decorators.http import require_POST

@login_required
@role_required('admin')
@require_POST
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

@login_required
@role_required('admin')
def admin_orders(request):
    orders_list = Order.objects.select_related(
        'client', 'artist__user', 'request'
    ).prefetch_related('submissions').order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)

    # Paginate 8 orders per page
    paginator = Paginator(orders_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'current_status': status_filter
    }
    return render(request, 'admin/orders.html', context)

@login_required
@role_required('admin')
def admin_payments(request):
    payments_list = Payment.objects.select_related('order__client', 'order__artist').order_by('-created_at')
    
    # Financial Summary
    total_escrow = Payment.objects.filter(status='held').aggregate(Sum('amount'))['amount__sum'] or 0
    total_released = Payment.objects.filter(status='released').aggregate(Sum('amount'))['amount__sum'] or 0
    
    paginator = Paginator(payments_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'payments': page_obj,
        'total_escrow': total_escrow,
        'total_released': total_released,
    }
    return render(request, 'admin/payments.html', context)

@login_required
@role_required('admin')
@require_POST
def delete_request_view(request, id):
    req = get_object_or_404(Request, id=id)
    req.delete()
    messages.success(request, "Request deleted successfully.")
    return redirect('admin_requests')

@login_required
@role_required('admin')
@require_POST
def delete_order_view(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    messages.success(request, "Order deleted successfully.")
    return redirect('admin_orders')

@login_required
@role_required('admin')
@require_POST
def delete_payment_view(request, id):
    payment = get_object_or_404(Payment, id=id)
    payment.delete()
    messages.success(request, "Payment deleted successfully.")
    return redirect('admin_payments')


@login_required
@role_required('admin')
def admin_disputes(request):
    disputes_list = Dispute.objects.select_related('order', 'raised_by').order_by('-created_at')
    
    paginator = Paginator(disputes_list, 10)
    page_number = request.GET.get('page')
    disputes = paginator.get_page(page_number)
    
    return render(request, 'admin/disputes.html', {'disputes': disputes})

@login_required
@role_required('admin')
def admin_dispute_detail(request, id):
    dispute = get_object_or_404(Dispute, id=id)
    order = dispute.order
    
    if request.method == "POST":
        action = request.POST.get('action')
        payment_service = PaymentService()
        
        try:
            if action == 'favor_client':
                # Refund client
                payment_service.refund_payment(order)
                dispute.status = Dispute.Status.RESOLVED
                dispute.save()
                messages.success(request, f"Dispute resolved in favor of the client. Order cancelled and ₹{order.amount} refunded.")
                
            elif action == 'favor_artist':
                # Release funds to artist
                payment_service.release_payment(order)
                order.status = Order.Status.COMPLETED
                order.save()
                dispute.status = Dispute.Status.RESOLVED
                dispute.save()
                messages.success(request, f"Dispute resolved in favor of the artist. Order completed and ₹{order.amount} released.")
                
            elif action == 'dismiss':
                # Resume workflow
                if order.submissions.exists():
                    order.status = Order.Status.SUBMITTED
                else:
                    order.status = Order.Status.IN_PROGRESS
                order.save()
                
                dispute.status = Dispute.Status.REJECTED
                dispute.save()
                messages.success(request, "Dispute dismissed. Order workflow resumed.")
                
        except Exception as e:
            messages.error(request, f"Error resolving dispute: {str(e)}")
            
        return redirect('admin_disputes')
        
    submissions = order.submissions.all()
    
    return render(request, 'admin/dispute_detail.html', {
        'dispute': dispute,
        'order': order,
        'submissions': submissions
    })