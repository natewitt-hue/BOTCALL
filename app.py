import os
import json
from flask import Flask, request, send_from_directory

app = Flask(__name__)

# MUST HAVE: A root route for Render's port scanner to find
@app.route('/')
def home():
    return "TSL Data Server is Active", 200

# Directory setup
DATA_DIR = os.path.join(os.getcwd(), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/export', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/export/<path:path>', methods=['POST', 'GET'])
def handle_all(path):
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True)
        if not data:
            return "No JSON", 400
        
        # Saves files like 'standings.json' or 'roster_123.json'
        clean_path = path.strip('/').split('/')[-1]
        filename = f"{clean_path}.json" if clean_path else "data.json"
        
        with open(os.path.join(DATA_DIR, filename), 'w') as f:
            json.dump(data, f)
        return f"Saved {filename}", 200

    # GET requests serve the data
    return send_from_directory(DATA_DIR, path)

if __name__ == "__main__":
    # This is ignored by Gunicorn but good for local testing
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
