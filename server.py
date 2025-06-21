from flask import Flask, request, send_from_directory, render_template_string
import os
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = '/storage/emulated/0/KutralUploads'

MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB
MIN_FREE_SPACE = 23 * 1024 * 1024 * 1024  # 23 GB mínimo libre

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_folder_size(folder):
    total = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

def free_space():
    stat = os.statvfs(UPLOAD_FOLDER)
    return stat.f_bsize * stat.f_bavail

def eliminar_archivos_antiguos():
    archivos = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)]
    archivos = [f for f in archivos if os.path.isfile(f)]
    archivos.sort(key=lambda x: os.path.getmtime(x))

    while free_space() < MIN_FREE_SPACE and archivos:
        archivo_a_borrar = archivos.pop(0)
        print(f"Borrando archivo antiguo: {os.path.basename(archivo_a_borrar)}")
        os.remove(archivo_a_borrar)

@app.route('/')
def index():
    espacio_usado = get_folder_size(UPLOAD_FOLDER) / (1024*1024*1024)
    espacio_libre = free_space() / (1024*1024*1024)

    alert = ""
    if espacio_libre < MIN_FREE_SPACE / (1024*1024*1024):
        alert = f"<p style='color:red;'>⚠️ Espacio bajo: quedan {espacio_libre:.2f} GB libres. Se eliminarán archivos antiguos automáticamente.</p>"

    return render_template_string("""
        <h1>Kütral 🔥</h1>
        {{ alert|safe }}
        <p>Espacio usado: {{ espacio_usado|round(2) }} GB</p>
        <p>Espacio libre: {{ espacio_libre|round(2) }} GB</p>

        <h2>Sube tu archivo (máx 1 GB):</h2>
        <form method="POST" action="/subir" enctype="multipart/form-data">
            <input type="file" name="archivo" required>
            <input type="submit" value="Subir">
        </form>
    """, espacio_usado=espacio_usado, espacio_libre=espacio_libre, alert=alert)

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files['archivo']
    if archivo:
        archivo.seek(0, os.SEEK_END)
        tamaño = archivo.tell()
        archivo.seek(0)

        if tamaño > MAX_FILE_SIZE:
            return f"Error: El archivo es demasiado grande (máx 1 GB). <a href='/'>Volver</a>"

        eliminar_archivos_antiguos()

        if free_space() < tamaño:
            return f"Error: No hay suficiente espacio. <a href='/'>Volver</a>"

        ruta = os.path.join(UPLOAD_FOLDER, archivo.filename)
        archivo.save(ruta)

        link = f"/descargar/{archivo.filename}"
        return f"Archivo subido correctamente.<br>Link de descarga: <a href='{link}'>{link}</a><br><br><a href='/'>Volver</a>"

    return "No se subió ningún archivo."

@app.route('/descargar/<nombre>')
def descargar(nombre):
    return send_from_directory(UPLOAD_FOLDER, nombre, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
