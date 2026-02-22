import os
import json
from flask import Flask, request, send_from_directory

app = Flask(__name__)

# Render uses /opt/render/project/src/ by default. 
# We'll use a local 'data' folder.
DATA_DIR = os.path.join(os.getcwd(), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/health')
def health_check():
    return "Alive", 200

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def handle_all(path):
    if request.method == 'POST':
        try:
            data = request.get_json(force=True, silent=True)
            if not data:
                return "No JSON data", 400

            # Clean the path to create a filename
            # e.g., /export/ps5/625743/standings -> standings.json
            clean_path = path.strip('/').replace('/', '_')
            filename = f"{clean_path}.json" if clean_path else "export.json"
            
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            print(f"DEBUG: Saved {filename}")
            return f"Received {filename}", 200
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return str(e), 500

    # GET requests: serve the file if it exists
    return send_from_directory(DATA_DIR, path)

if __name__ == "__main__":
    # This part is only for local testing; Render uses Gunicorn
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
