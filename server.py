from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'CharmBot server running'

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    message = data.get('message', '')
    style = data.get('style', '')
    use_style = data.get('use_style', False)

    # Простейший ответ-заглушка
    return jsonify(reply=f"Generated reply for: '{message}' in style '{style}'")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)