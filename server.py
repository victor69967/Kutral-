from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

# Carpeta local para guardar archivos temporalmente
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Config Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'kutral-463611-d6aae10c66cb.json'  # Tu archivo JSON

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# ID de la carpeta en Google Drive donde guardarás los archivos
GOOGLE_DRIVE_FOLDER_ID = '10wh12hNfUl-NTKBFr0J6IHQZAzgeUah7'


@app.route('/')
def index():
    return render_template_string("""
        <h1>Kütral 🔥 (Render + Google Drive)</h1>
        <h2>Sube tu archivo (máx 1 GB):</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Subir">
        </form>
    """)


@app.route('/upload', methods=['POST'])
def upload():
    archivo = request.files.get('file')
    if not archivo:
        return "No se subió ningún archivo."

    # Guardar archivo local temporalmente
    local_path = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(local_path)

    # Subir a Google Drive
    file_metadata = {
        'name': archivo.filename,
        'parents': [GOOGLE_DRIVE_FOLDER_ID]
    }
    media = MediaIoBaseUpload(io.FileIO(local_path, 'rb'), mimetype=archivo.mimetype)
    drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Borra archivo local para no llenar el disco
    os.remove(local_path)

    # URL pública (opcional, se puede ajustar permisos en Drive para compartir)
    file_id = drive_file.get('id')
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

    return f"Archivo subido correctamente a Google Drive.<br>Link de descarga directa:<br><a href='{download_url}'>{download_url}</a><br><br><a href='/'>Volver</a>"


if __name__ == '__main__':
    # Puerto para Render, asignado por variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
