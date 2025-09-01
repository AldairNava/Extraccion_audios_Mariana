import ftplib
from datetime import datetime, timedelta
import time

ftp_config = {
    'host': '192.168.50.37',
    'user': 'rpaback1',
    'passwd': 'Cyber123',
    'remote_dir': 'Audios'
}

#true para ver cuanto s se borran(no se borrara nada en true)
DRY_RUN = False
# Para probar rápido, limita la cantidad de archivos a procesar (None = sin límite)
MAX_FILES_DEBUG = None  # por ejemplo 500

# Ventana de borrado (cámbialo a 90 para ~3 meses)
CUT_DAYS = 60

# --- Utilidades ---

def connect_ftp(cfg):
    print("[INFO] Conectando al FTP...")
    ftp = ftplib.FTP()
    # Timeout de conexión
    ftp.connect(cfg['host'], 21, timeout=30)
    print("[INFO] Conexión establecida, autenticando...")
    ftp.login(cfg['user'], cfg['passwd'])
    ftp.set_pasv(True)
    print(f"[INFO] Navegando a carpeta: {cfg['remote_dir']}")
    ftp.cwd(cfg['remote_dir'])
    # Timeout del socket para evitar cuelgues en comandos largos
    try:
        ftp.sock.settimeout(10)  # segundos
        print("[INFO] Timeout de socket establecido a 10s.")
    except Exception:
        pass
    return ftp

def parse_list_line(line: str):
    """
    Parsea una línea típica de LIST (estilo Unix).
    Devuelve (name, is_dir). Si no puede parsear, intenta extraer el nombre.
    """
    # Formato común: drwxr-xr-x  2 owner group    4096 Aug  7 12:34 Nombre con espacios
    is_dir = line.startswith('d')
    # Nombre suele ir tras la 8ª columna (índice 8)
    parts = line.split(None, 8)
    name = parts[-1] if len(parts) >= 9 else line.split()[-1]
    return name, is_dir

def list_names_and_types_via_LIST(ftp: ftplib.FTP):
    print("[INFO] Listando con LIST para distinguir archivos de directorios...")
    entries = []

    def cb(line):
        name, is_dir = parse_list_line(line)
        # saltar pseudo entradas
        if name in ('.', '..'):
            return
        entries.append((name, is_dir))

    ftp.retrlines('LIST', cb)
    print(f"[INFO] LIST devolvió {len(entries)} entradas (archivos y carpetas).")
    return entries

def get_mtime_with_retry(ftp: ftplib.FTP, name: str, retries: int = 2):
    """
    Intenta MDTM con reintentos y pequeños sleeps.
    Devuelve datetime o None si no se pudo.
    """
    for attempt in range(1, retries + 1):
        try:
            resp = ftp.sendcmd(f"MDTM {name}")  # '213 YYYYMMDDHHMMSS'
            stamp = resp.strip().split()[-1]
            return datetime.strptime(stamp, "%Y%m%d%H%M%S")
        except Exception as e:
            if attempt < retries:
                time.sleep(0.2 * attempt)  # backoff chiquito
            else:
                # último intento fallido
                print(f"[WARN] MDTM falló para '{name}' (intentos={retries}): {e}")
                return None

# --- Flujo principal ---

def main():
    now = datetime.now()
    cutoff = now - timedelta(days=CUT_DAYS)

    ftp = connect_ftp(ftp_config)
    try:
        print("[INFO] Obteniendo lista de entradas (LIST)...")
        entries = list_names_and_types_via_LIST(ftp)

        # Filtrar sólo archivos
        files = [(n, d) for (n, d) in entries if not d]
        total = len(files)
        print(f"[INFO] Total de archivos detectados: {total}")

        if MAX_FILES_DEBUG is not None:
            files = files[:MAX_FILES_DEBUG]
            print(f"[INFO] DEBUG: procesando sólo los primeros {len(files)} archivos.")

        archivos = []
        print("[INFO] Consultando MDTM por archivo (esto puede tardar)…")
        for i, (name, _) in enumerate(files, start=1):
            mtime = get_mtime_with_retry(ftp, name, retries=2)
            archivos.append((name, mtime))
            if i % 100 == 0:
                print(f"[DEBUG] MDTM procesados: {i}/{total}")

        print(f"[INFO] MDTM completado para {len(archivos)} archivos.")

        # Ordenar por fecha (None va al final)
        archivos.sort(key=lambda x: (x[1] is None, x[1]))

        print("\n=== LISTA (más antiguos primero) ===")
        for name, mtime in archivos[:200]:  # no saturar la salida; muestra 200 primeros
            fecha_txt = mtime.strftime("%Y-%m-%d %H:%M:%S") if mtime else "SIN_FECHA"
            print(f"{fecha_txt}  |  {name}")
        if len(archivos) > 200:
            print(f"[INFO] … y {len(archivos) - 200} más.")

        # Elegibles a borrar
        to_delete = [(n, t) for n, t in archivos if t is not None and t < cutoff]
        print(f"\n[INFO] Candidatos a borrar (> {CUT_DAYS} días, antes de {cutoff.strftime('%Y-%m-%d')}): {len(to_delete)}")

        for idx, (name, mtime) in enumerate(to_delete, start=1):
            if DRY_RUN:
                print(f"[DRY-RUN] BORRAR: {name} (modificado: {mtime})  [{idx}/{len(to_delete)}]")
            else:
                try:
                    ftp.delete(name)
                    print(f"[OK] Borrado: {name} (modificado: {mtime})  [{idx}/{len(to_delete)}]")
                except Exception as e:
                    print(f"[ERROR] al borrar {name}: {e}")

        if DRY_RUN:
            print("\n*** DRY_RUN activo: no se borró nada. Cambia DRY_RUN=False para ejecutar el borrado. ***")

    finally:
        print("[INFO] Cerrando conexión FTP...")
        try:
            ftp.quit()
            print("[INFO] Conexión cerrada.")
        except Exception:
            pass

if __name__ == "__main__":
    main()
