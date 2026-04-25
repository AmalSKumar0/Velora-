from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from users.models import *
from commissions.models import *
from core.models import Tag
from payments.models import Payment
from users.decorators import role_required
from django.http import FileResponse


@login_required
@role_required('client')
def client_dash(request):
    return render(request,'client/dashboard.html',
    {
        'tags':Tag.objects.all()
    })
    
@login_required
@role_required('client')
def clinet_view_individual_work(request,order_id):

    order = Order.objects.get(
        id=order_id,
    )

    if request.method == "POST":

        action = request.POST.get("action")
        comment = request.POST.get("comment")
        subid = request.POST.get("subid")

        if action not in ["approved", "changes_requested"]:
            messages.error(request, "Invalid action")
            return redirect("clinet_view_individual_work", order.id)

        if not comment:
            if action == "approved":
                comment = "Work approved by client"
            else:
                comment = "Changes requested by client"

        sub = Submission.objects.get(id=subid, order=order)


        if SubmissionReview.objects.filter(submission=sub).exists():
            messages.error(request, "Already reviewed this submission")
            return redirect("clinet_view_individual_work", order.id)

        with transaction.atomic():
            
            SubmissionReview.objects.create(
                reviewed_by=request.user,
                action=action,
                comment=comment,
                submission=sub
            )
            
            if action == "approved":
                order.status = "approved" 
            else:
                order.status = "revision_requested" 
                count = order.revision_count + 1
                order.revision_count = count

            order.save()


    submission = Submission.objects.filter(order=order).first()
    subrev = SubmissionReview.objects.filter(submission=submission).first()
    review = Review.objects.filter(order=order).first()


    return render(request, 'client/request/individual_work.html', {
        'order': order,
        'submission':submission,
        'subrev':subrev,
        'review':review,
        'tags':Tag.objects.all()
    })


@login_required
@role_required('client')
def add_review(request):
    if request.method == "POST":

        order_id = request.POST.get('orderid')
        order = Order.objects.get(id=order_id)
        artist = order.artist
        client = request.user
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            order = order,
            client = client,
            artist = artist,
            rating = rating,
            comment = comment
        )

        messages.success(request,"Review added successfully")
        return redirect("clinet_view_individual_work", order.id)
    
    return redirect('login')


@login_required
@role_required('client')
def download_final(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    order = submission.order

    if request.user != order.client:
        raise Http404("Not allowed")

    if order.status != "completed":
        raise Http404("Order not completed")

    return FileResponse(
        submission.original_file.open(),
        as_attachment=True,
        filename=submission.original_file.name
    )

@login_required
@role_required('client')
def complete_order(request, order_id):

    order = Order.objects.get(id=order_id)
    if order.status != "approved":
        messages.error(request, "Order is not approved yet")
        return redirect("clinet_view_individual_work", order.id)

    req = order.request
    payment = Payment.objects.filter(order=order).first()

    with transaction.atomic():

        order.status = 'completed'
        order.save()

        req.status = 'completed'
        req.save()

        if payment:
            payment.status = 'released'
            payment.save()

    messages.success(request, "Order completed and payment released to the artist")

    return redirect("clinet_view_individual_work", order.id)