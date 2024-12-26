from collections.abc import Iterable
from webob import Request
from parse  import parse
from requests import Session
from wsgiadapter import WSGIAdapter
import inspect
from jinja2 import Environment, FileSystemLoader
import os
from whitenoise import WhiteNoise
from middleware import Middleware
from response import Response

class Api:

    def __init__(self, template_dir="templates", static_dir="static") -> None:
        self.routes = {}
        self.template_env = Environment(loader=FileSystemLoader(os.path.abspath(template_dir)))
        self.exception_handler = None
        self.whitenoise = WhiteNoise(application=self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)
    
    def __call__(self, environ, start_response) -> Iterable[str]:
        # return self.whitenoise(environ, start_response)
        request_path = environ["PATH_INFO"]
        if request_path.startswith("/static"):
            environ["PATH_INFO"] = request_path[len("/static"):]
            return self.whitenoise(environ, start_response)
        
        return self.middleware(environ, start_response)
    
    def add_middleware(self, middleware_class):
        self.middleware.add(middleware_class)
        
    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)
        
        return response(environ, start_response)
    

    def add_exception_handler(self, e):
        self.exception_handler = e
    
    def template(self, template_name, context=None):
        if not context:
            context = {}
        return self.template_env.get_template(template_name).render(**context)
    
    def add_route(self, path, handler, allowed_methods=None):
        if path in self.routes:
                raise AssertionError('Path is already registered.')
        if not allowed_methods:
            allowed_methods = ["get", "post", "put", "path", "delete", "options"]
        self.routes[path] = {
            "handler": handler,
            "allowed_methods": allowed_methods
        }
    
    def route(self, path, allowed_methods=None):
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler
        return wrapper

    
    def handle_request(self, request):
        response = Response()
        try:
            handler_data, args = self.find_handler(request.path)
            if handler_data:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                request_method = request.method.lower()
                if  inspect.isclass(handler):
                    handler = getattr(handler(), request_method, None)
                    if handler is None:
                        raise AttributeError(f'Method is not defiened, {request_method}')
                else:
                    if request_method not in allowed_methods:
                        raise AttributeError(f'Method is not defiened, {request_method}')
                handler(request, response, **args)
            else:
                self.default_response(response)
        except Exception as e:
            if not self.exception_handler:
                raise e
            else:
                self.exception_handler(request, response, e)
        
        return response
    
    def find_handler(self, request_path):
        for path, handler_data in self.routes.items():
            parsed = parse(path, request_path)
            if parsed is not None:
                return handler_data, parsed.named
            
        return None, None
    
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Not Found"

    def test_session(self, base_url="http://testserver"):
        session = Session()
        session.mount(prefix=base_url, adapter=WSGIAdapter(self))
        return session