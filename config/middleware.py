import time

class ArtificialDelayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Add artificial delay AFTER view is processed
        time.sleep(5)  # Delay in seconds
        return response
