from api import Api

app = Api(template_dir="templates")

def custom_exception(request, response, e):
    response.text = "Ups, something went wrong!"
    response.status_code = 404

app.add_exception_handler(custom_exception)

@app.route('/home')
def home(request, response):
    response.text = "This is home page"

@app.route('/about', allowed_methods=["post"])
def about(request, response):
    response.text = "This is about page"

@app.route('/hello/{name}')
def hello(request, response, name):
    response.text = f"Hello, {name}"

@app.route('/do_staff')
class DoStaff:
    def get(self, request, response):
        response.text = "Doing the staff"

    def post(self, request, response):
        response.text = "Posting the staff"


@app.route('/do_other_staff')
class DoStaff:
    def get(self, request, response):
        response.body = app.template(template_name="test_template.html", context={"hello":"Elsevar"}).encode()

    def post(self, request, response):
        response.text = "Posting the staff"

@app.route('/exception')
def excp(request, response):
    raise Exception()