from django.utils import translation

class ForceEnglishMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        translation.activate('en')
        request.LANGUAGE_CODE = 'en'
        response = self.get_response(request)
        translation.deactivate()
        return response