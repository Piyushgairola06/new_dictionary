from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, static_folder='static')
CORS(app)

# Load Garhwali translations
try:
    with open('garhwali_translations.json', 'r', encoding='utf-8') as f:
        garhwali_translations = json.load(f)
except FileNotFoundError:
    garhwali_translations = {}

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/define/<word>', methods=['GET'])
def define_word(word):
    try:
        # Get English definition
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        if response.status_code == 200:
            data = response.json()[0]

            # Add Garhwali translation if available
            garhwali = garhwali_translations.get(word.lower())
            if garhwali:
                data['garhwali'] = garhwali

            return jsonify(data)
        else:
            return jsonify({'error': 'Word not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional: Route to add translations manually
@app.route('/api/add_translation', methods=['POST'])
def add_translation():
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
