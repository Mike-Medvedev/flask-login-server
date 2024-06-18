from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import db_utils
import pyodbc
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, verify_jwt_in_request, get_jwt_identity
import secrets
import logging

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)
jwt = JWTManager(app)
app.config.from_pyfile('config.py')
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_ALGORITHM'] = app.config['ALGO']

logging.basicConfig(level=logging.INFO)

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
            access_token = create_access_token(identity=request_data['username'])
            app.logger.info(f"Created access token: {access_token}")
            print(access_token)
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


@app.route('/verify', methods=["POST"])
@jwt_required()
def verify():
    try:
        verify_jwt_in_request()  # Verify JWT in the request
        current_user = get_jwt_identity()
        print('Current user:', current_user)
        return jsonify(message='Token successfully verified'), 200
    except Exception as e:
        print('Error verifying jwt in request:', e)
        return jsonify(message=str(e)), 401

# if __name__ == '__app__':
#     app.run(debug=True)

   