import ftplib
import socket
from datetime import datetime, timedelta

# --- Configuración del FTP ---
ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'
}

def borrar_antiguos_60_dias():
    ahora  = datetime.now()
    umbral = ahora - timedelta(days=60)
    print(f"[+] Umbral de eliminación (60 días atrás): {umbral.strftime('%Y-%m-%d %H:%M:%S')}")

    # Forzar timeout para evitar bloqueos
    socket.setdefaulttimeout(30)

    # 1) Conexión FTP
    ftp = ftplib.FTP(timeout=30)
    ftp.connect(ftp_config['host'])
    ftp.login(ftp_config['user'], ftp_config['passwd'])
    ftp.cwd(ftp_config['remote_dir'])
    print(f"[+] Conectado a carpeta remota: {ftp_config['remote_dir']}")

    # 2) Listado de archivos
    try:
        archivos = ftp.nlst()
    except Exception as e:
        print(f"[!] Error al listar directorio: {e}")
        ftp.quit()
        return

    borrados = 0
    # 3) Procesar cada archivo
    for nombre in archivos:
        if nombre in ('.', '..'):
            continue

        # Obtener fecha de modificación con MDTM
        try:
            resp      = ftp.sendcmd(f"MDTM {nombre}")  # "213 YYYYMMDDHHMMSS"
            fecha_str = resp[4:].strip()
            fecha_mod = datetime.strptime(fecha_str, "%Y%m%d%H%M%S")
        except Exception as e:
            print(f"    · No se pudo MDTM de {nombre}: {e}")
            continue

        dias_antiguedad = (ahora - fecha_mod).days

        # 4) Si encontramos un archivo con EXACTAMENTE 60 días, detenemos la búsqueda
        if dias_antiguedad <= 60:
            print(f"[!] Encontrado archivo con antigüedad de 60 días → '{nombre}'. Deteniendo búsqueda.")
            break

        # 5) Si es más antiguo que 60 días, borrarlo
        if fecha_mod < umbral:
            try:
                ftp.delete(nombre)
                borrados += 1
                print(f"    ✓ BORRADO: {nombre} (antigüedad: {dias_antiguedad} días)")
            except Exception as e:
                print(f"    ✗ Error al borrar {nombre}: {e}")
        else:
            print(f"    · Mantiene: {nombre} (antigüedad: {dias_antiguedad} días)")

    # 6) Cerrar conexión e imprimir resumen
    ftp.quit()
    print(f"[+] Total de archivos borrados: {borrados}")

if __name__ == "__main__":
    borrar_antiguos_60_dias()
