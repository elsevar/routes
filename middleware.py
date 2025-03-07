from typing import Any
from webob import Request

class Middleware:
    def __init__(self, app) -> None:
        self.app = app
    
    def __call__(self, environ, start_response) -> Any:
        requset = Request(environ)
        response = self.app.handle_request(requset)
        return response(environ, start_response)

    def add(self, middleware_class):
        self.app = middleware_class(self.app)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def handle_request(self, request):
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)
        return response