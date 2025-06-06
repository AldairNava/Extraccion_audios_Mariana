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

def obtener_nombres_audios_pendientes():
    conexion = mysql.connector.connect(**db_config)
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT audio_name FROM audios where owner = 'izzi' and status = 'Asignado' ORDER BY id DESC;")
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

                # Verificar si el archivo ya existe y eliminarlo
                if os.path.exists(destino_archivo):
                    try:
                        os.remove(destino_archivo)
                        print(f"Archivo existente eliminado: {destino_archivo}")
                    except Exception as e:
                        print(f"No se pudo eliminar el archivo existente: {e}")

                shutil.move(ruta_archivo, directorio_destino)
                print(f"Movido: {ruta_archivo} a {directorio_destino}")
                archivo_encontrado = True
                break
        if not archivo_encontrado:
            print(f"Archivo no encontrado: {nombre_audio}")

def subir_archivos_ftp():
    archivos_subidos = 0
    try:
        # Conexión FTP
        ftp = FTP()
        ftp.connect(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['passwd'])
        ftp.cwd(ftp_config['remote_dir'])
        
        # Conexión a la base de datos para la actualización de estatus
        conexion_db = mysql.connector.connect(**db_config)
        cursor_db = conexion_db.cursor()

        for archivo in os.listdir(directorio_destino):
            ruta_archivo = os.path.join(directorio_destino, archivo)
            try:
                # Subir al FTP
                with open(ruta_archivo, 'rb') as file:
                    ftp.storbinary(f'STOR {archivo}', file)
                    print(f"Subido a la carpeta ftp: {archivo}")

                # Eliminar archivo local
                os.remove(ruta_archivo)
                print(f"Eliminado archivo local: {ruta_archivo}")
                archivos_subidos += 1

                # -- NUEVO: Actualizar en la BD el estado a "Pendiente"
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
                    print(f"Error al actualizar estado en BD para {archivo}: {err_db}")

            except error_perm as e:
                print(f"Permiso denegado al subir el archivo {archivo}: {e}")
                send_msg(f"Permiso denegado al subir el archivo {archivo}: {e}")
            except all_errors as e:
                print(f"Error general al subir el archivo {archivo}: {e}")
                send_msg(f"Error general al subir el archivo {archivo}: {e}")

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
        nombres_audios_pendientes = obtener_nombres_audios_pendientes()
        mover_archivos(nombres_audios_pendientes)
        subir_archivos_ftp()
        print("ARCHIVOS SUBIDOS")
        print("Esperando Siguiente Carga de Audios......")
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
        send_msg(f"Error en el proceso principal: {e}")
