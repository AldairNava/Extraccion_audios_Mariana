import mysql.connector
from ftplib import FTP, all_errors

# --- Configuración de la base de datos ---
db_config = {
    'host': '192.168.51.210',
    'user': 'root',
    'password': '',
    'database': 'audios_dana'
}

# --- Configuración del FTP ---
ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'  # Carpeta en el FTP donde están los audios
}

def obtener_nombres_asignados():
    """
    Recupera de la tabla audios todos los nombres de archivo cuyo status sea 'Asignado' o 'not found audio'
    con fecha igual a ayer.
    """
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT audio_name 
            FROM audios 
            WHERE status IN ('not found audio', 'Asignado') 
            AND DATE(fecha_llamada) >= DATE_SUB(CURDATE(), INTERVAL 3 DAY);
        """)
        resultados = cursor.fetchall()
        return [fila[0] for fila in resultados]
    finally:
        conexion.close()

def actualizar_status(audio_name, nuevo_status):
    """
    Actualiza el campo status de un audio dado.
    """
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE audios SET status = %s WHERE audio_name = %s",
            (nuevo_status, audio_name)
        )
        conexion.commit()
    finally:
        conexion.close()

def main():
    # 1) Obtener lista de audios pendientes de FTP
    nombres = obtener_nombres_asignados()
    if not nombres:
        print("No hay audios con status 'Asignado'.")
        return

    # 2) Conectarse al FTP y obtener lista de archivos
    try:
        ftp = FTP(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['passwd'])
        ftp.cwd(ftp_config['remote_dir'])
        archivos_ftp = ftp.nlst()  # lista de nombres de archivos en la carpeta remota
        ftp.quit()
    except all_errors as e:
        print(f"Error al conectar o listar FTP: {e}")
        return

    # 3) Para cada audio, comprobar existencia y actualizar DB
    for nombre in nombres:
        if nombre in archivos_ftp:
            actualizar_status(nombre, 'Pendiente')
            print(f"Encontrado en FTP → '{nombre}': status actualizado a 'Pendiente'")
        else:
            print(f"No encontrado en FTP → '{nombre}' (se mantiene status 'Asignado')")

if __name__ == '__main__':
    main()
