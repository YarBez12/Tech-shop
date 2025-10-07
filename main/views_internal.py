from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def run_sync(request):
    token = request.headers.get("X-Cron-Token") or request.POST.get("token")
    if not token or token != getattr(settings, "SYNC_CRON_TOKEN", None):
        return HttpResponseForbidden("Forbidden")

    from products.tasks import sync_views_from_redis, sync_favourites_to_db

    sync_views_from_redis()
    sync_favourites_to_db()

    return JsonResponse({"ok": True})