from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import *
from commissions.models import *
from core.models import Tag
from users.decorators import role_required




@login_required
@role_required('artist')
def artist_dash(request):
    if not hasattr(request.user, 'artist_profile'):
        messages.error(request,'complete the profile first!')
        return redirect('create_artist_profile')

    artist_profile = request.user.artist_profile
    tags = artist_profile.tags.all()
    requests = Request.objects.filter(
        tags__in=tags
    ).distinct().prefetch_related('tags', 'images')

    return render(request, 'artist/dashboard.html', {
        'requests': requests,
        'artist_tags': tags
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

