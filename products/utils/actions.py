from users.models import Action
from django.contrib.contenttypes.models import ContentType

def create_action(user, verb, target=None):
    existing = Action.objects.filter(user=user, verb=verb)
    if target:
        ct = ContentType.objects.get_for_model(target)
        existing = existing.filter(target_ct=ct, target_id=target.id)
    if existing.exists():
        return False

    action = Action(user=user, verb=verb, target=target)
    action.save()
    return True

def delete_action(user, verb, target=None):
    actions = Action.objects.filter(user=user, verb=verb)
    if target:
        ct = ContentType.objects.get_for_model(target)
        actions = actions.filter(target_ct=ct, target_id=target.id)
    actions.delete()