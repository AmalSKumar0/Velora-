from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            if "admin" in roles and request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.role in roles:
                return view_func(request, *args, **kwargs)

            messages.error(request,"Unauthorized")
            return redirect('login')

        return _wrapped_view
    return decorator