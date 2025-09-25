class StashAnonSessionKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()
        if not request.user.is_authenticated:
            request.session['anon_session_key'] = request.session.session_key
        return self.get_response(request)