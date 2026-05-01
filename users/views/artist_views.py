from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from django.db import transaction
from commissions.models import *
from django.db.models import Max
from core.models import Tag
from users.decorators import role_required
from core.services.watermark import generate_preview



@login_required
@role_required('artist')
def artist_dash(request):

    if not hasattr(request.user, 'artist_profile'):
        messages.error(request,'complete the profile first!')
        return redirect('create_artist_profile')

    artist_profile = request.user.artist_profile
    tags = artist_profile.tags.all()

    requests = Request.objects.filter(
        tags__in=tags,
        status='open'
    ).distinct().prefetch_related('tags', 'images')

    for req in requests:
        if Proposal.objects.filter(artist=artist_profile,request=req):
            req.has_proposed = True
        else:
            req.has_proposed = False


    return render(request, 'artist/dashboard.html', {
        'requests': requests,
        'artist_tags': tags
    })


@login_required
@role_required('artist')
def artist_profile_view(request):

    artist_profile, created = ArtistProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        
        # 1. Update Base User Fields
        user.username = request.POST.get('username', user.username)
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        user.save()

        # 2. Update ArtistProfile Fields
        artist_profile.display_name = request.POST.get('display_name', artist_profile.display_name)
        artist_profile.bio = request.POST.get('bio', artist_profile.bio)
        artist_profile.portfolioURL = request.POST.get('portfolioURL', artist_profile.portfolioURL)
        artist_profile.is_available = 'is_available' in request.POST
        artist_profile.save()
        
        messages.success(request, 'Your artist profile has been updated successfully!')
        return redirect('artist_profile')

    portfolio_items = artist_profile.portfolio.prefetch_related('tags').order_by('-created_at')

    context = {
        'artist': artist_profile,
        'portfolio_items': portfolio_items
    }
    return render(request, 'artist/profile.html', context)

@login_required
def delete_portfolio_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(PortfolioItem, id=item_id, artist__user=request.user)
        item.delete()
        messages.success(request, "Artwork deleted from your portfolio.")
    return redirect('my_artist_profile')


@login_required
@role_required('artist')
def view_my_work(request):

    artist_profile = request.user.artist_profile

    orders = Order.objects.filter(
        artist=artist_profile
    ).select_related(
        "request",
        "client",
        "proposal"
    ).order_by("-created_at")

    return render(request, 'artist/request/my_work.html', {
        'orders': orders
    })

@login_required
@role_required('artist')
def individual_work(request,order_id):

    artist_profile = request.user.artist_profile

    order = Order.objects.get(
        id=order_id,
        artist = artist_profile
    )

    if request.method == "POST":
        
        original_file = request.FILES.get('image')
        preview_file = generate_preview(original_file,"Art by Velora")


        last_version = Submission.objects.filter(order=order).aggregate(
                    Max('version')
                )['version__max'] or 0   
        with transaction.atomic():

            sub = Submission.objects.create(
                order=order,
                version=last_version + 1,
                preview_file=preview_file,
                original_file=original_file
            ) 

            order.status = "submitted"
            order.save()


    submissions = order.submissions.prefetch_related("reviews").all()
    return render(request, 'artist/request/individual_work.html', {
        'order': order,
        'submissions': submissions
    })


@login_required
@role_required('artist')
def create_artist_profile(request):
    user = request.user

    if hasattr(user, 'artist_profile'):
        return redirect('add_portfolio_item')  

    if user.role != 'artist':
        messages.error(request,"You are not an artist!")
        return redirect('home')

    if request.method == 'POST':

        display_name = request.POST.get('display_name')
        bio = request.POST.get('bio')
        portfolioURL = request.POST.get('portfolioURL')
        is_available = request.POST.get('is_available') == 'on'
        tag_ids = request.POST.getlist('tags')  # multiple select

        art = ArtistProfile.objects.create(
            user=user,
            display_name=display_name,
            bio=bio,
            portfolioURL=portfolioURL,
            is_available=is_available
        )
        art.tags.set(tag_ids)

        return redirect('add_portfolio_item')
    tags = Tag.objects.all()

    return render(request, 'artist/complete_profile.html',
    {
        'tags':tags
    })
    

@login_required
@role_required('artist')
def add_portfolio_item(request):
    user = request.user

    if not hasattr(user, 'artist_profile'):
        messages.error(request,'complete the profile first!')
        return redirect('create_artist_profile')

    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        tag_ids = request.POST.getlist('tags[]')

        item = PortfolioItem.objects.create(
            artist=user.artist_profile,
            title=title,
            image=image
        )

        item.tags.set(tag_ids)


        messages.success(request,"Portfolio added sucessfully")
        return redirect('add_portfolio_item')

    tags = Tag.objects.all()
    return render(request, 'artist/create_portfolio.html', {'tags': tags})

