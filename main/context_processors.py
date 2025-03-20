from allauth.socialaccount.models import SocialApp
from conf import settings

def socialaccount(request):
    apps = SocialApp.objects.filter(sites=settings.SITE_ID)
    return {'socialaccount_providers': apps}