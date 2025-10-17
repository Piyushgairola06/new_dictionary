from flask import Flask, jsonify, send_from_directory, request, session
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", "mysecretkey")  # for session handling
CORS(app, supports_credentials=True)

# Load Garhwali translations
try:
    with open('garhwali_translations.json', 'r', encoding='utf-8') as f:
        garhwali_translations = json.load(f)
except FileNotFoundError:
    garhwali_translations = {}

# Hardcoded Admin credentials (you can later move them to env vars)
ADMIN_ID = "admin"
ADMIN_PASS = "12345"

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# ✅ User/Role Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    role = data.get('role')
    user_id = data.get('id')
    password = data.get('password')

    if role == "admin":
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session['role'] = 'admin'
            return jsonify({"message": "Admin logged in successfully"})
        else:
            return jsonify({"error": "Invalid admin credentials"}), 401
    elif role == "user":
        session['role'] = 'user'
        return jsonify({"message": "User logged in"})
    else:
        return jsonify({"error": "Invalid role"}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('role', None)
    return jsonify({"message": "Logged out"})

# ✅ Dictionary Definition
@app.route('/api/define/<word>', methods=['GET'])
def define_word(word):
    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        if response.status_code == 200:
            data = response.json()[0]
            garhwali = garhwali_translations.get(word.lower())
            if garhwali:
                data['garhwali'] = garhwali
            return jsonify(data)
        else:
            return jsonify({'error': 'Word not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Protected Translation Addition (only Admin)
@app.route('/api/add_translation', methods=['POST'])
def add_translation():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        data = request.get_json()
        word = data.get('word', '').lower()
        translation = data.get('garhwali', '')
        if not word or not translation:
            return jsonify({'error': 'Both word and translation are required'}), 400

        garhwali_translations[word] = translation
        with open('garhwali_translations.json', 'w', encoding='utf-8') as f:
            json.dump(garhwali_translations, f, ensure_ascii=False, indent=4)

        return jsonify({'message': f'Translation for "{word}" added successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
