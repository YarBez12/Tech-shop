from users.models import NotificationState, Action
from products.models import Product
from django.utils import timezone
from datetime import datetime, timedelta, timezone as dt_timezone
from django.contrib.contenttypes.models import ContentType


def min_date():
    return datetime(1970, 1, 1, tzinfo=dt_timezone.utc)

def notification_counts(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    state, _ = NotificationState.objects.get_or_create(user=user)

    brand_ids = list(user.subcriptions.values_list('brand_id', flat=True))
    product_ids = list(user.products.values_list('id', flat=True))
    unread_news = 0
    unread_actions = 0
    if brand_ids:
        since_news = state.last_seen_news or min_date()
        since_window = timezone.now() - timedelta(days=14)
        unread_news = (
            Product.objects
            .filter(brand_id__in=brand_ids)
            .filter(updated_at__gte=since_window, updated_at__gt=since_news)
            .exclude(user=user)
            .count()
        )

    if product_ids:
        since_actions = state.last_seen_actions or min_date()
        product_ct = ContentType.objects.get_for_model(Product)
        unread_actions = (
            Action.objects
            .filter( target_ct=product_ct, target_id__in=product_ids, created__gt=since_actions)
            .exclude(user=user)
            .count()
        )

    return {
        'unread_news_count': unread_news,
        'unread_actions_count': unread_actions,
        'total_notifications': unread_news + unread_actions
    }