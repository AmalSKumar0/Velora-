from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Tag
from payments.models import Payment
from django.db import transaction
from django.db.models import Count
from users.decorators import role_required
from django.db.models import Count, Exists, OuterRef

@login_required
@role_required('client')
def request_view(request):
    
    paid_exists = Payment.objects.filter(
        order__request=OuterRef('pk'),
        status__in=['held', 'released'] 
    )

    order_exists = Order.objects.filter(
        request=OuterRef('pk')
    )

    requests = Request.objects.filter(
        client=request.user
    ).prefetch_related(
        'tags',
        'images',
        'order_set__payment'
    ).annotate(
        proposal_count=Count('proposals'),
        has_order=Exists(order_exists),
        is_paid=Exists(paid_exists)
    ).order_by('-created_at')

    return render(request, 'client/request/requests.html', {
        'requests': requests,
        'tags':Tag.objects.all()
    })


@login_required
@role_required('client')
def add_new_request(request):

    tags = Tag.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget_min = request.POST.get('budget_min')
        budget_max = request.POST.get('budget_max')
        tag_ids = request.POST.getlist('tags')  # multiple select
        images = request.FILES.getlist('images')

        if int(budget_min) > int(budget_max):
            messages.error(request,"Minimum budget should be more then that of Maximum limit")
            return redirect('create_request')

        if len(images) > 4:
            messages.error(request, "You can upload up to 4 images")
            return redirect('create_request')


        for img in images:
            if not img.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed")
                return redirect('create_request')

            if img.size > 1 * 1024 * 1024:
                messages.error(request, "Each image must be under 1MB")
                return redirect('create_request')


        with transaction.atomic():

            req = Request.objects.create(
                client=request.user, 
                title=title,
                description=description,
                budget_min=budget_min,
                budget_max=budget_max,
            )
            req.tags.set(tag_ids)

            image_objs = [
                RequestImage(request=req, image=img)
                for img in images
            ]

            RequestImage.objects.bulk_create(image_objs)
            
    return redirect('all_request')


@login_required
@role_required('artist')
def send_new_proposal(request, id):
    req = get_object_or_404(Request, id=id)

    artist_profile = request.user.artist_profile

    if Proposal.objects.filter(request=req, artist=artist_profile).exists():
        messages.error(request, "You already submitted a proposal")
        return redirect('artistDashboard')

    if request.method == "POST":
        price = request.POST.get('price')
        message = request.POST.get('message')
        delivery_days = request.POST.get('delivery_days')

        Proposal.objects.create(
            request=req,
            artist=artist_profile,
            price=price,
            message=message,
            delivery_days=delivery_days
        )

        return redirect('artistDashboard')

    return render(request, 'artist/request/send_proposal.html', {
        'req': req,
        'tags':Tag.objects.all()
    })

@login_required
@role_required('client')
def view_all_proposal(request, id):
    req = get_object_or_404(Request, id=id, client=request.user)

    proposals = Proposal.objects.filter(
        request=req,
    )
    return render(request, "client/request/all_proposals.html", {
        'proposals': proposals,
        'tags':Tag.objects.all()
    })

@login_required
@role_required('client')
def accept_proposal(request, id):

    proposal = get_object_or_404(Proposal, id=id)
    req = proposal.request

    if req.client != request.user:
        messages.error(request, "You are not allowed to accept this proposal")
        return redirect('all_request')

    if req.status != "open":
        messages.error(request, "Request already processed")
        return redirect('all_request')

    Order.objects.filter(request=req).delete()

    with transaction.atomic():

        order = Order.objects.create(
            request=req,  
            proposal=proposal,
            client=request.user,
            artist=proposal.artist,
            amount=proposal.price
        )
        
    return redirect('create_payment',order_id=order.id)

    messages.success(request, "Proposal accepted")
    return redirect('all_request')