from .models import User


def associate_by_email(strategy, details, user=None, *args, **kwargs):
    if user:
        return {"user": user}
    email = details.get("email")
    if not email:
        return
    try:
        existing_user = User.objects.get(email=email)
    except User.DoesNotExist:
        return
    return {"user": existing_user}


def save_user_details_once(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and is_new:
        updated = False
        if details.get('first_name'):
            user.first_name = details['first_name']
            updated = True
        if details.get('last_name'):
            user.last_name = details['last_name']
            updated = True
        if updated:
            user.save()