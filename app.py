import os
import zipfile
from flask import Flask, request, send_from_directory, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/export', methods=['POST'])
def handle_export():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Save and Extract
    zip_path = os.path.join(UPLOAD_FOLDER, "export.zip")
    file.save(zip_path)
    
    with zip_file.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(UPLOAD_FOLDER)
    
    return "Export successful!", 200

@app.route('/data/<filename>', methods=['GET'])
def get_data(filename):
    # This allows your bot to "look" here for players.json, teams.json, etc.
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
