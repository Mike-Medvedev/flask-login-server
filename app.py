from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import db_utils
import pyodbc
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import secrets

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)
jwt = JWTManager(app)
secret_key = secrets.token_urlsafe(32)
# with open('/Users/michaelmedvedev/Coding/keys/pubkeyfile.pem', 'r') as key_file:
#     app.config['JWT_SECRET_KEY'] = key_file.read().strip()
app.config['JWT_SECRET_KEY'] = secret_key

@app.route("/")
def handle_get():
     # try:
    #     db_utils.insert_form()
    # except:
    #     print('error occured')
    response = jsonify({'message': 'Hello From Flask'})
    return response

@app.route('/login', methods=["POST"])
def login():
    request_data = request.get_json()
    try:  
        if 'username' in request_data and 'password' in request_data:
            data = db_utils.login(request_data, bcrypt)
            access_token = create_access_token(identity=data.get('username'))
            return jsonify({"data": data, "access_token": access_token}), 200
        else:
            raise ValueError('Invalid content')
    except Exception as e:
        print('error occured trying to login', e)
        response = jsonify({'Error': str(e)})
        return response, 500

@app.route('/signup', methods=["POST"])
def signup():
    request_data = request.get_json()
    try:  
        if 'username' in request_data and 'password' in request_data:
            data = db_utils.signup(request_data, bcrypt)
            return data, 200
        else:
            raise ValueError('Invalid content')

    except pyodbc.IntegrityError as e:
        print(f'Integrity Error: {e}')
        response = jsonify({"Error": "Username taken please use a different one"})
        return response, 409

    except Exception as e:
        print('error occured trying to signup', e)
        response = jsonify({'Error': str(e)})
        return response, 500

   