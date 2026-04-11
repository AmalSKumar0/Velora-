from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.decorators import login_required
from core.models import Tag
from django.db import transaction


@login_required
def request_view(request):
    requests = Request.objects.filter(client=request.user).prefetch_related(
        'tags',
        'images'
    ).order_by('-created_at')
    
    return render(request,'client/request/requests.html',{
        'requests':requests,
    })


@login_required
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

    return render(request,'client/request/addrequest.html', {'tags': tags})


