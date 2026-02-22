import os
import zipfile
import shutil
from flask import Flask, request, send_from_directory

app = Flask(__name__)
# Render has a limited ephemeral file system, so we use /tmp or a local 'data' folder
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/export', methods=['POST'])
def receive_export():
    # Snallabot typically sends the zip as the request body or a file field
    file_data = request.data
    zip_path = os.path.join(DATA_DIR, 'league_data.zip')
    
    with open(zip_path, 'wb') as f:
        f.write(file_data)
    
    # Unzip immediately so the JSONs are accessible
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        return "Success: Unzipped Snallabot export", 200
    except Exception as e:
        return f"Error unzipping: {str(e)}", 500

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
