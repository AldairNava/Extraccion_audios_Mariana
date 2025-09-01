import mysql.connector
import os
import shutil
from ftplib import FTP, error_perm, all_errors
from Tele import send_msg
import subprocess

# --- Configuraciones de BD y FTP ---

db_configs = {
    'avena': {
        'host': '192.168.51.210',
        'user': 'root',
        'password': 'thor',
        'database': 'marianaavena'
    },
    'mariana': {
        'host': '192.168.51.210',
        'user': 'root',
        'password': 'thor',
        'database': 'audios_dana'
    }
}

ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'
}

directorios_busqueda = [
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_retenciones",
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios",
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios_apo",
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_televentas",
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte",
    r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte_apo"
]

directorio_destino  = r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_filtrados"
directorio_subidos  = r"C:\Extraccion_Mariana_Continuo\audios_subidos"

tablas_por_base = {
    'avena': ['audios'],
    'mariana': ['audios', 'audiosSpeech']
}

# --- Funciones de BD ---

def obtener_nombres_pendientes_por_tabla(db_key, tabla):
    cfg = db_configs[db_key]
    nombres = []
    conn = mysql.connector.connect(**cfg)
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT audio_name FROM {tabla} WHERE status in ('Asignado','Error FTP','not found audio')"
        )
        for (audio_name,) in cur.fetchall():
            nombres.append(audio_name)
        cur.close()
    finally:
        conn.close()
    return nombres

def actualizar_estado(audio_name, nuevo_estado, db_key, tabla, contadores):
    cfg = db_configs[db_key]
    conn = mysql.connector.connect(**cfg)
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE {tabla} SET status = %s, ip = NULL WHERE audio_name = %s",
            (nuevo_estado, audio_name)
        )
        if cur.rowcount == 0:
            contadores['no_encontrados'] += 1
            contadores['no_encontrados_lista'].append((db_key, tabla, audio_name, nuevo_estado))
        else:
            contadores['actualizados'] += 1
        conn.commit()
        cur.close()
    except Exception as e:
        contadores['errores'].append(f"Error actualizando [{db_key}.{tabla}] para {audio_name}: {e}")
    finally:
        conn.close()

def actualizar_estado_todas_tablas(audio_name, nuevo_estado, contadores):
    for db_key, tablas in tablas_por_base.items():
        for tabla in tablas:
            actualizar_estado(audio_name, nuevo_estado, db_key, tabla, contadores)

# --- Funciones de archivos ---

def mover_archivos(nombres_tabla, db_key, tabla):
    os.makedirs(directorio_destino, exist_ok=True)
    movidos = []
    contadores = {
        'movidos': 0,
        'no_encontrados': 0,
        'actualizados': 0,
        'errores': [],
        'no_encontrados_lista': []
    }

    for nombre in nombres_tabla:
        encontrado = False
        for d in directorios_busqueda:
            ruta_src = os.path.join(d, nombre)
            if os.path.exists(ruta_src):
                ruta_dst = os.path.join(directorio_destino, nombre)
                if os.path.exists(ruta_dst):
                    os.remove(ruta_dst)
                shutil.move(ruta_src, directorio_destino)
                movidos.append((nombre, db_key, tabla))
                contadores['movidos'] += 1
                encontrado = True
                break
        if not encontrado:
            actualizar_estado(nombre, 'not found audio', db_key, tabla, contadores)

    # Prints resumidos
    if contadores['movidos'] > 0:
        print(f"[{db_key}.{tabla}] {contadores['movidos']} audios movidos a audios_filtrados.")
    if contadores['no_encontrados'] > 0:
        print(f"[{db_key}.{tabla}] No se encontraron {contadores['no_encontrados']} audios para actualizar a 'not found audio'.")
    if contadores['errores']:
        print(f"[{db_key}.{tabla}] Errores: {len(contadores['errores'])} (ver detalle en logs)")

    return movidos

def subir_archivos_ftp(movidos, para_todas_tablas=True):
    os.makedirs(directorio_subidos, exist_ok=True)
    total = 0
    errores = []
    permisos = 0
    generales = 0

    try:
        ftp = FTP(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['passwd'])
        ftp.cwd(ftp_config['remote_dir'])

        for nombre, db_key, tabla in movidos:
            ruta_local = os.path.join(directorio_destino, nombre)
            if not os.path.exists(ruta_local):
                continue
            try:
                with open(ruta_local, 'rb') as f:
                    ftp.storbinary(f'STOR {nombre}', f)
                ruta_sub = os.path.join(directorio_subidos, nombre)
                shutil.move(ruta_local, ruta_sub)
                total += 1
                # Actualizar estatus
                contadores = {
                    'no_encontrados': 0,
                    'no_encontrados_lista': [],
                    'actualizados': 0,
                    'errores': []
                }
                if para_todas_tablas:
                    actualizar_estado_todas_tablas(nombre, 'Pendiente', contadores)
                else:
                    actualizar_estado(nombre, 'Pendiente', db_key, tabla, contadores)

            except error_perm as e:
                permisos += 1
                errores.append(f"{nombre} (permiso denegado)")
                contadores = {
                    'no_encontrados': 0,
                    'no_encontrados_lista': [],
                    'actualizados': 0,
                    'errores': []
                }
                if para_todas_tablas:
                    actualizar_estado_todas_tablas(nombre, 'Error FTP', contadores)
                else:
                    actualizar_estado(nombre, 'Error FTP', db_key, tabla, contadores)

            except all_errors as e:
                generales += 1
                errores.append(f"{nombre} ({e})")
                contadores = {
                    'no_encontrados': 0,
                    'no_encontrados_lista': [],
                    'actualizados': 0,
                    'errores': []
                }
                if para_todas_tablas:
                    actualizar_estado_todas_tablas(nombre, 'Error FTP', contadores)
                else:
                    actualizar_estado(nombre, 'Error FTP', db_key, tabla, contadores)

        ftp.quit()
    except all_errors as e:
        print(f"Error conectando al FTP: {e}")
        send_msg(f"Error conectando al FTP: {e}")

    print(f"Total archivos subidos exitosamente: {total}")
    send_msg(f"Total archivos subidos exitosamente: {total}")
    if permisos > 0:
        print(f"Errores de permisos FTP: {permisos}")
    if generales > 0:
        print(f"Errores generales FTP: {generales}")

    if errores:
        resumen = f"{len(errores)} audios no se pudieron subir por error en FTP (ver consola/logs)."
        send_msg(resumen)

def procesar_audios_filtrados():
    print("\nProcesando audios rezagados en audios_filtrados...")
    movidos = []
    for archivo in os.listdir(directorio_destino):
        ruta_archivo = os.path.join(directorio_destino, archivo)
        if os.path.isfile(ruta_archivo):
            movidos.append((archivo, '', ''))

    if movidos:
        subir_archivos_ftp(movidos)
    else:
        print("No hay audios rezagados en audios_filtrados.")

# --- Flujo principal ---

if __name__ == "__main__":
    try:
        movidos_total = []
        for db_key, tablas in tablas_por_base.items():
            for tabla in tablas:
                print(f"Procesando {db_key}.{tabla} ...")
                nombres = obtener_nombres_pendientes_por_tabla(db_key, tabla)
                if nombres:
                    movidos = mover_archivos(nombres, db_key, tabla)
                    movidos_total.extend(movidos)
                else:
                    print(f"No hay audios con status 'Asignado' en {db_key}.{tabla}.")

        if movidos_total:
            subir_archivos_ftp(movidos_total, para_todas_tablas=True)
        else:
            print("No se movió ningún archivo; nada que subir.")

        procesar_audios_filtrados()

        print("Ejecutando buscar_fpt.py ...")
        subprocess.run(['python', 'buscar_ftp.py'], check=True)

    except Exception as e:
        print(f"Error en el proceso principal: {e}")
        send_msg(f"Error en el proceso principal: {e}")
