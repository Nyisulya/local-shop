from .models import POSUser

def pos_user(request):
    user_id = request.session.get('pos_user_id')
    if user_id:
        try:
            return {'current_pos_user': POSUser.objects.get(id=user_id)}
        except POSUser.DoesNotExist:
            pass
    return {'current_pos_user': None}
