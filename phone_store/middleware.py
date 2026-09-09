import time


class RequestTimingMiddleware:
    """Adds a lightweight server-timing header for observing request duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - started_at) * 1000
        response["X-Request-Duration-ms"] = f"{duration_ms:.2f}"
        return response
