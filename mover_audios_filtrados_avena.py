import mysql.connector
import os
import shutil
from ftplib import FTP, error_perm, all_errors
from Tele import send_msg
import requests
import threading

db_config = {
    'host': '192.168.51.210',
    'user': 'root',
    'password': '',
    'database': 'marianaavena'
}

ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'
}

# Carpeta donde se moverán los audios subidos
directorio_subidos = r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\audios_subidos"

def obtener_nombres_audios_pendientes():
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT audio_name FROM audios "
            "WHERE owner = 'izzi' AND status = 'Asignado' "
            "ORDER BY id DESC;"
        )
        resultados = cursor.fetchall()
        nombres_audios = [fila[0] for fila in resultados]
        cursor.close()
        print(nombres_audios)
        return nombres_audios
    finally:
        conexion.close()

directorios_busqueda = [
    r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_rar_retenciones",
    r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_rar_servicios",
    r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_rar_servicios_apo",
    r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_rar_soporte",
    r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_rar_soporte_apo"
]

directorio_destino = r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\carpeta_de_audios\audios_filtrados"

def mover_archivos(nombres_audios):
    for nombre_audio in nombres_audios:
        archivo_encontrado = False
        for directorio in directorios_busqueda:
            ruta_archivo = os.path.join(directorio, nombre_audio)
            if os.path.exists(ruta_archivo):
                destino_archivo = os.path.join(directorio_destino, nombre_audio)

                if os.path.exists(destino_archivo):
                    try:
                        os.remove(destino_archivo)
                        print(f"Archivo existente eliminado: {destino_archivo}")
                    except Exception as e:
                        print(f"No se pudo eliminar el archivo existente: {e}")

                shutil.move(ruta_archivo, directorio_destino)
                print(f"Movido: {ruta_archivo} → {directorio_destino}")
                archivo_encontrado = True
                break
        if not archivo_encontrado:
            print(f"Archivo no encontrado: {nombre_audio}")

def subir_archivos_ftp():
    # Asegurar que exista la carpeta de subidos
    os.makedirs(directorio_subidos, exist_ok=True)

    archivos_subidos = 0
    try:
        ftp = FTP()
        ftp.connect(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['passwd'])
        ftp.cwd(ftp_config['remote_dir'])

        # Conexión DB para actualizar estado
        conexion_db = mysql.connector.connect(**db_config)
        cursor_db = conexion_db.cursor()

        for archivo in os.listdir(directorio_destino):
            ruta_archivo = os.path.join(directorio_destino, archivo)
            try:
                # Subir al FTP
                with open(ruta_archivo, 'rb') as f:
                    ftp.storbinary(f'STOR {archivo}', f)
                print(f"Subido a FTP: {archivo}")

                # Mover a carpeta de subidos
                destino_subido = os.path.join(directorio_subidos, archivo)
                shutil.move(ruta_archivo, destino_subido)
                print(f"Movido a subidos: {destino_subido}")
                archivos_subidos += 1

                # Actualizar estado en BD
                try:
                    sql_update = """
                        UPDATE audios
                        SET status = 'Pendiente'
                        WHERE audio_name = %s
                    """
                    cursor_db.execute(sql_update, (archivo,))
                    conexion_db.commit()
                    print(f"Estado actualizado a 'Pendiente' para {archivo}")
                except Exception as err_db:
                    print(f"Error actualizando BD para {archivo}: {err_db}")

            except error_perm as e:
                print(f"Permiso denegado al subir {archivo}: {e}")
                send_msg(f"Permiso denegado al subir {archivo}: {e}")
            except all_errors as e:
                print(f"Error general al subir {archivo}: {e}")
                send_msg(f"Error general al subir {archivo}: {e}")

        # Cerrar conexiones
        cursor_db.close()
        conexion_db.close()
        ftp.quit()

    except all_errors as e:
        print(f"Error en la conexión FTP: {e}")
        send_msg(f"Error en la conexión FTP: {e}")

    print(f"Total de archivos subidos: {archivos_subidos}")

if __name__ == "__main__":
    try:
        nombres = obtener_nombres_audios_pendientes()
        mover_archivos(nombres)
        subir_archivos_ftp()
        print("ARCHIVOS PROCESADOS")
        print("Esperando siguiente carga de audios...")
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
        send_msg(f"Error en el proceso principal: {e}")
