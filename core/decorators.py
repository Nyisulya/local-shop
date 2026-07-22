from django.shortcuts import redirect
from django.http import JsonResponse
from functools import wraps
from .models import POSUser

def pos_login_required(allowed_roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = request.session.get('pos_user_id')
            if not user_id:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Authentication required. Please login.'}, status=401)
                return redirect(f'/login/?next={request.path}')
            
            try:
                user = POSUser.objects.get(id=user_id)
            except POSUser.DoesNotExist:
                del request.session['pos_user_id']
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'User not found. Please login.'}, status=401)
                return redirect(f'/login/?next={request.path}')
            
            # Attach user to request for convenience
            request.pos_user = user
            
            if allowed_roles:
                # admin has access to everything
                if user.role != 'admin' and user.role not in allowed_roles:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                        return JsonResponse({'error': 'Unauthorized role.'}, status=403)
                    return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
