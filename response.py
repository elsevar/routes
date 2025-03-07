from webob import Response as WebObResponse
import json

class Response:
    def __init__(self) -> None:
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b""
        self.status_code = 200

    def __call__(self, environ, start_response):
        self.set_up_response_body_and_header()
        response = WebObResponse(body=self.body, content_type=self.content_type, status=self.status_code)
        return response(environ, start_response)

    def set_up_response_body_and_header(self):
        if self.json is not None:
            self.body = json.dumps(self.json).encode("UTF-8")
            self.content_type = "application/json"

        if self.html is not None:
            self.body = self.html.encode("UTF-8")
            self.content_type = "text/html"

        if self.text is not None:
            self.body = self.text.encode("UTF-8")
            self.content_type = "text/plain"