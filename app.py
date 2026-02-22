import os
import json
from flask import Flask, request, send_from_directory

app = Flask(__name__)
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# This catches everything Snallabot sends (standings, rushing, etc.)
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    # Determine a filename based on the URL path (e.g., 'standings')
    parts = path.split('/')
    filename = parts[-1] if parts else "export"
    
    # Get the data from Snallabot
    data = request.get_json(force=True, silent=True)
    
    if data:
        file_path = os.path.join(DATA_DIR, f"{filename}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print(f"Saved: {filename}.json")
        return "Data Received", 200
    
    return "No JSON data found", 400

# This allows WittGPT to read the files
@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
