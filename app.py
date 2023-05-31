from flask import Flask, request, jsonify
import requests
import dotenv
import os
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# Inisialisasi Firebase
cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)

# Endpoint untuk register
@app.route('/register', methods=['POST'])
def register():
    email = request.json['email']
    password = request.json['password']

    try:
        # Membuat user baru dengan Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )
        return jsonify({'message': 'Registrasi berhasil', 'localId': user.uid})

    except Exception as e:
        return jsonify({'message': 'Registrasi gagal', 'error': str(e)}), 400

# Endpoint untuk login
@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    try:
        # Melakukan proses login dengan Firebase Authentication
        user = auth.get_user_by_email(email)
        if user:
            # user = auth.sign_in_with_email_and_password(email, password)
            # return jsonify({'message': 'Login berhasil', 'localId': user.uid})
            dotenv.load_dotenv()
            api_key= os.getenv("FIREBASE_API_KEY")
            login_url="https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}".format(api_key)
            requests_body={"email":email , "password":password}
            # print(requests_body)
            rest = requests.post(login_url,json=requests_body)
            return jsonify({'message': 'Login berhasil', "data":rest.json()})
        else:
            return jsonify({'message': 'Login gagal', 'error': 'User tidak ditemukan'}), 401

    except Exception as e:
        return jsonify({'message': 'Login gagal', 'error':str(e)}),401

if __name__ == '__main__':
    app.run(debug=True)