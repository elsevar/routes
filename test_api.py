import pytest
from api import Api


def test_add_route(api):

    @api.route('/about')
    def about(request, response):
        response.text = "This is about page"

    with pytest.raises(AssertionError):
        @api.route('/about')
        def about(request, response):
            response.text = "This is about page"

def test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "This is about page"

    @api.route('/about')
    def about(request, response):
        response.text = RESPONSE_TEXT

    response = client.get('http://testserver:8000/about')

    assert response.text ==  RESPONSE_TEXT

def test_requests_with_parameter(api, client):
    RESPONSE_TEXT1 = "Hello, Elsevar"
    RESPONSE_TEXT2 = "Hello, Eli"
    @api.route('/hello/{name}')
    def about(request, response, name):
        response.text = f"Hello, {name}"

    response = client.get('http://testserver:8000/hello/Elsevar')
    assert response.text ==  RESPONSE_TEXT1

    response = client.get('http://testserver:8000/hello/Eli')
    assert response.text ==  RESPONSE_TEXT2

def test_page_not_found(api, client):
    RESPONSE_TEXT = "Not Found"
    response = client.get('http://testserver:8000/does-not-exist')
    assert response.text ==  RESPONSE_TEXT
    assert response.status_code == 404

def test_class_based_handlers(api, client):
    @api.route('/do_staff')
    class DoStaff:
        def get(self, request, response):
            response.text = "Doing the staff"

        def post(self, request, response):
            response.text = "Posting the staff"

    assert client.get("http://testserver:8000/do_staff").text == "Doing the staff"
    assert client.post("http://testserver:8000/do_staff").text == "Posting the staff"

def test_wrong_http_method(api, client):
    @api.route('/do_staff')
    class DoStaff:
        def post(self, request, response):
            response.text = "Posting the staff"

    with pytest.raises(AttributeError):
        resp = client.get("http://testserver:8000/do_staff")

def test_django_style_router(api, client):
    def about(request, response):
        response.text = f"Doing the staff"

    api.add_route('/do_staff', about)

    assert client.get("http://testserver:8000/do_staff").text == "Doing the staff"            
    

def test_template_render(api, client):
    def about(request, response):
        response.body = api.template("test_template.html", context={"hello": "hello"}).encode()

    api.add_route('/do_staff', about)

    response = client.get("http://testserver:8000/do_staff")

    assert "text/html" in response.headers["Content-Type"]
    assert "hello" in response.text 


def test_custom_exception_handler(api, client):
    def custom_exception_handler(request, response, exception):
        response.text = "Ups!"

    api.add_exception_handler(custom_exception_handler)

    @api.route("/do")
    def do(request, response):
       raise Exception()
    
    response = client.get("http://testserver:8000/do")
    assert response.text == "Ups!"

def test_static_file_not_found(client):
    assert client.get("http://testserver:8000/main.css").status_code == 404


STATIC_DIR = "css"
STATIC_FILE = "main.css"
STATIC_CONTENT = "body {background-color: red}"
def _create_asset(static_dir):
    asset = static_dir.mkdir(STATIC_DIR).join(STATIC_FILE)
    asset.write(STATIC_CONTENT)
    return asset


def test_static_file_fetched(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp('static')
    _create_asset(static_dir)
    
    api = Api(static_dir=str(static_dir))
    client = api.test_session()
    response = client.get(f"http://testserver:8000/static/{STATIC_DIR}/{STATIC_FILE}")

    assert response.status_code == 200
    assert response.text == STATIC_CONTENT


def test_middleware(api, client):
    response_processed = False
    request_processed = False

    from middleware import Middleware

    class TestMiddleware(Middleware):
        def process_request(self, request):
            nonlocal request_processed
            request_processed = True
        
        def process_response(self, request, response):
            nonlocal response_processed
            response_processed = True

    @api.route("/do")
    def do(request, response):
       response.text = "Middleware test"

    api.add_middleware(TestMiddleware)
    response = client.get("http://testserver:8000/do")

    assert response_processed == True
    assert request_processed == True

def test_allowed_methods(api, client):

    @api.route("/do", allowed_methods = ["post"])
    def do(request, response):
       response.text = "Allowed methods"

    with pytest.raises(AttributeError):
        client.get("http://testserver:8000/do")

    client.post("http://testserver:8000/do")

def test_json_response(api, client):

    @api.route("/json")
    def do(request, response):
       response.json = {"key1": "value1", "key2": "value2"}

    response = client.get("http://testserver:8000/json")
    assert response.status_code == 200
    assert response.json() == {"key1": "value1", "key2": "value2"}
    assert response.headers["Content-Type"] == "application/json"


def test_html_response(api, client):

    @api.route("/html")
    def do(request, response):
       response.html = api.template("test_template.html", context={"hello": "hello"})

    response = client.get("http://testserver:8000/html")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "hello" in response.text


def test_text_response(api, client):

    @api.route("/text")
    def do(request, response):
       response.text = "Just simple text"

    response = client.get("http://testserver:8000/text")
    assert response.status_code == 200
    assert "text/plain" in response.headers["Content-Type"]
    assert "Just simple text" in response.text

def text_body_response(api, client):
    @api.route("/body")
    def do(request, response):
        response.body = b"Just simple text"
        response.content_type = "text/plain"


    response = client.get("http://testserver:8000/body")
    assert response.status_code == 200
    assert "text/plain" in response.headers["Content-Type"]
    assert "Just simple text" in response.text




