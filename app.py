import os
import json
from flask import Flask, request, send_from_directory

app = Flask(__name__)
# Using /tmp ensures write permissions on Render's ephemeral disk
DATA_DIR = os.path.join(os.getcwd(), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def handle_all(path):
    if request.method == 'POST':
        # Snallabot sends data as JSON
        data = request.get_json(force=True, silent=True)
        if not data:
            return "No JSON found", 400

        # Create a filename based on the URL path
        # Example: /ps5/625743/team/774242335/roster -> roster_774242335.json
        parts = path.strip('/').split('/')
        
        if 'roster' in parts:
            # Identifies which team this roster belongs to
            team_id = parts[-2] if len(parts) > 1 else "unknown"
            filename = f"roster_{team_id}.json"
        else:
            # Uses the last part of the URL (e.g., standings, leagueteams)
            filename = f"{parts[-1]}.json" if parts else "export.json"

        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        print(f"Successfully saved: {filename}")
        return f"Saved {filename}", 200

    # If it's a GET request, try to serve the file from the data folder
    return send_from_directory(DATA_DIR, path)

if __name__ == "__main__":
    # Render uses port 10000 by default
    app.run(host='0.0.0.0', port=10000)
