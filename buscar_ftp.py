import mysql.connector
from ftplib import FTP, all_errors

# --- Configuración de la base de datos ---
db_config = {
    'host': '192.168.51.210',
    'user': 'root',
    'password': 'thor',
    'database': 'audios_dana'
}

# --- Configuración del FTP ---
ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'
}

def obtener_nombres_asignados(tabla):
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute(f"""
            SELECT audio_name 
            FROM {tabla} 
            WHERE status IN ('not found audio', 'Asignado','Error FTP') 
            AND DATE(fecha_llamada) >= DATE_SUB(CURDATE(), INTERVAL 3 DAY);
        """)
        resultados = cursor.fetchall()
        return [fila[0] for fila in resultados]
    finally:
        conexion.close()

def actualizar_status(audio_name, nuevo_status, tabla):
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            f"UPDATE {tabla} SET status = %s, ip = NULL WHERE audio_name = %s",
            (nuevo_status, audio_name)
        )
        conexion.commit()
    finally:
        conexion.close()

def main():
    tablas = ["audios", "audiosSpeech"]
    archivos_a_revisar = []  # Tupla (nombre, tabla)

    for tabla in tablas:
        nombres = obtener_nombres_asignados(tabla)
        archivos_a_revisar.extend([(nombre, tabla) for nombre in nombres])

    if not archivos_a_revisar:
        print("No hay audios pendientes en ninguna tabla.")
        return

    try:
        ftp = FTP(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['passwd'])
        ftp.cwd(ftp_config['remote_dir'])
        archivos_ftp = set(ftp.nlst())
        ftp.quit()
    except all_errors as e:
        print(f"Error al conectar o listar FTP: {e}")
        return

    # --- Contadores por tabla ---
    resumen = {tabla: {"encontrados": 0, "no_encontrados": 0} for tabla in tablas}

    for nombre, tabla in archivos_a_revisar:
        if nombre in archivos_ftp:
            actualizar_status(nombre, 'Pendiente', tabla)
            resumen[tabla]["encontrados"] += 1
        else:
            resumen[tabla]["no_encontrados"] += 1

    # --- Solo prints resumen al final ---
    for tabla in tablas:
        if resumen[tabla]["encontrados"] > 0:
            print(f"[{tabla}] {resumen[tabla]['encontrados']} archivos encontrados en FTP y actualizados a 'Pendiente'")
        if resumen[tabla]["no_encontrados"] > 0:
            print(f"[{tabla}] {resumen[tabla]['no_encontrados']} archivos NO encontrados en FTP (se mantiene status actual)")

if __name__ == '__main__':
    main()
