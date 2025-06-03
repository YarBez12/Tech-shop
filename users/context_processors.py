from users.models import NotificationState, Action
from products.models import Product
from django.utils import timezone


def notification_counts(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    state, _ = NotificationState.objects.get_or_create(user=user)

    brand_ids = user.subcriptions.values_list('brand_id', flat=True)
    two_weeks_ago = timezone.now() - timezone.timedelta(days=14)
    news = Product.objects.filter(brand_id__in=brand_ids, updated_at__gte=two_weeks_ago)
    unread_news = news.filter(updated_at__gt=state.last_seen_news or timezone.datetime.min).count()

    product_ids = user.products.all().values_list('id', flat=True)
    unread_actions = Action.objects.filter(target_id__in=product_ids, created__gt=state.last_seen_actions or timezone.datetime.min).exclude(user=user).count()

    return {
        'unread_news_count': unread_news,
        'unread_actions_count': unread_actions,
        'total_notifications': unread_news + unread_actions
    }