import os
import json
from flask import Flask, request, send_from_directory

app = Flask(__name__)

# Directory setup
DATA_DIR = os.path.join(os.getcwd(), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def home():
    # Show a list of all files currently stored on the server
    files = os.listdir(DATA_DIR)
    file_list = "<br>".join([f'<a href="/{f}">{f}</a>' for f in files]) if files else "No files yet. Run export in Snallabot."
    return f"<h1>TSL Data Server Active</h1><p>Files available:</p>{file_list}", 200

# 1. Receiver for Snallabot (POSTs)
@app.route('/export/<path:path>', methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def handle_post(path):
    data = request.get_json(force=True, silent=True)
    if not data:
        return "No JSON received", 400
    
    parts = path.strip('/').split('/')
    
    # Smart Naming: Differentiates rosters so they don't overwrite each other
    if 'roster' in parts:
        # Path is usually: /export/ps5/625743/team/TEAMID/roster
        # We grab the TEAMID (second to last part)
        team_id = parts[-2] if len(parts) > 1 else "unknown"
        filename = f"roster_{team_id}.json"
    else:
        # Standard files (standings, teamstats, passing, etc.)
        filename = f"{parts[-1]}.json"
    
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        json.dump(data, f)
    
    print(f"Captured: {filename}")
    return f"Success: {filename}", 200

# 2. File Server for WittGPT/Browser (GETs)
@app.route('/<path:filename>', methods=['GET'])
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
