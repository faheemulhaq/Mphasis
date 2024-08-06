from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
CORS(app)

# Sample user data
users = {}

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Helper function to check password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in users:
        return jsonify({"message": "User already exists"}), 400
    
    users[email] = {
        'password': hash_password(password)
    }
    return jsonify({"message": "User registered successfully"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = users.get(email)
    
    if not user or not check_password(password, user['password']):
        return jsonify({"message": "Invalid email or password"}), 401
    
    return jsonify({"message": "Login successful"}), 200

if __name__ == '__main__':
    app.run(port=8501, debug=True)
