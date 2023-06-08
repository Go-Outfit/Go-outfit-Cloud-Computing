from flask import Flask, request, jsonify
import requests
import dotenv
import os
import uuid
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore

app = Flask(__name__)

# Inisialisasi Firebase
cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)

# Endpoint untuk register dan menyimpan account di firestore
@app.route('/register', methods=['POST'])
def register():
    db = firestore.client()
    acc = db.collection('account')
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    try:
        # Membuat user baru dengan Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
        )
        random_number = str(uuid.uuid4())[:15]
        account_id = "account-" + random_number
        acc_data = {
            'username': username,
            'email': email,
            'password': password,
        }
        acc.document(account_id).set(acc_data)
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
    app.run(debug=True, host='0.0.0.0', port=7000)
