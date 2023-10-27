from chalice import Chalice
from chalice import IAMAuthorizer

app = Chalice(app_name='api')
authorizer = IAMAuthorizer()

@app.route('/')
def index():
    return {'Bem vindo a aplicação': 'GameAssetsStore'}

@app.route('/iam-auth', methods=['GET'], authorizer=authorizer)
def authenticated():
    return {"success": True}

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
