import os
import sys
import threading
import pandas as pd
import mysql.connector
from send2trash import send2trash

# ——— Configuración ———
BASE_AUDIO_PATH = r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana"

# Subcarpetas donde buscar MP3
AUDIO_SUBFOLDERS = [
    "audios_filtrados",
    "audios_rar_retenciones",
    "audios_rar_servicios",
    "audios_rar_servicios_apo",
    "audios_rar_soporte",
    "audios_rar_soporte_apo",
]

# Pares (subcarpeta_de_datos, tabla_destino)
DATA_FOLDERS = [
    ("archivos_rar/servicios_rar",            "reporte_audios_servicios"),
    ("archivos_rar/soporte_rar",              "reporte_audios_soporte"),
    ("archivos_rar/retenciones_rar",          "reporte_audios_retenciones"),
    ("archivos_rar/servicios_apodaca_rar",    "reporte_audios_servicios_apodaca"),
    ("archivos_rar/soporte_apodaca_rar",      "reporte_audios_soporte_apodaca"),
]

DB_CONFIG = {
    "host": "192.168.51.210",
    "user": "root",
    "password": "",
    "database": "audios_dana",
    "connection_timeout": 90,
}

# ——— Funciones auxiliares ———
def find_csv_file(directory: str) -> str | None:
    """Busca un único .csv en el directorio y devuelve su ruta."""
    for fn in os.listdir(directory):
        if fn.lower().endswith(".csv"):
            return os.path.join(directory, fn)
    return None

def audio_valido(external_id: str) -> bool:
    """Comprueba si existe un .mp3 ≥ 5KB para el ID dado."""
    for sub in AUDIO_SUBFOLDERS:
        path = os.path.join(BASE_AUDIO_PATH, sub, f"{external_id}.mp3")
        if os.path.isfile(path) and os.path.getsize(path) >= 5 * 1024:
            return True
    return False

def load_data_to_db(csv_path: str, table: str) -> None:
    """Carga datos filtrados desde CSV a MySQL, maneja NaN → NULL y borra el CSV al final."""
    # Leer solo columnas necesarias
    cols = ["External ID", "Interaction Time", "Duration",
            "Metadata: agentId", "Metadata: Cuenta", "Metadata: CasoNegocio"]
    df = pd.read_csv(csv_path, usecols=cols)
    df.columns = ["External_ID", "Interaction_Time", "Duration",
                  "Metadata_agentId", "Metadata_Cuenta", "Metadata_CasoNegocio"]

    # Convertir todos los NaN a None para que sean NULL en MySQL
    df = df.where(pd.notna(df), None)

    # Filtrar solo filas cuyo audio sea válido
    registros = [
        (row.External_ID,
         row.Interaction_Time,
         row.Duration,
         row.Metadata_agentId,
         row.Metadata_Cuenta,
         row.Metadata_CasoNegocio)
        for _, row in df.iterrows()
        if audio_valido(str(row.External_ID))
    ]
    omitidos = len(df) - len(registros)

    # Temporizador de timeout para la conexión
    timer = threading.Timer(90.0, lambda: (print("Timeout: no se conectó a la BD en 90's."), sys.exit()))
    timer.start()

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = (
            f"INSERT INTO {table} "
            "(External_ID, Interaction_Time, Duration, Metadata_agentId, Metadata_Cuenta, Metadata_CasoNegocio) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        insertados = fallidos = 0
        print(f"Iniciando inserción en tabla `{table}`...")
        for row in registros:
            try:
                cursor.execute(query, row)
                insertados += 1
            except mysql.connector.Error as e:
                print(f"  ❌ Error al insertar {row}: {e}")
                fallidos += 1

        conn.commit()
        print(f"✅ Insertados: {insertados}, ❌ Fallidos: {fallidos}, ⚠️ Omitidos: {omitidos}")
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error de conexión o SQL: {e}")
    finally:
        timer.cancel()

    # Mover el CSV a la papelera
    try:
        send2trash(csv_path)
        print(f"📁 Archivo enviado a papelera: {csv_path}")
    except Exception as e:
        print(f"Error al eliminar CSV: {e}")

def main(arg: str) -> None:
    """Punto de entrada: recibe índice 0–4, procesa el CSV correspondiente."""
    try:
        idx = int(arg)
    except ValueError:
        print("El argumento debe ser un número entero (0–4).")
        return

    if not (0 <= idx < len(DATA_FOLDERS)):
        print("Índice fuera de rango. Debe ser entre 0 y 4.")
        return

    subcarpeta, tabla = DATA_FOLDERS[idx]
    directorio = os.path.join(BASE_AUDIO_PATH, subcarpeta)
    print(f"🔍 Buscando CSV en: {directorio}")
    csv_file = find_csv_file(directorio)

    if csv_file:
        print(f"✅ CSV encontrado: {csv_file}\n→ Cargando a `{tabla}`...")
        load_data_to_db(csv_file, tabla)
    else:
        print(f"❌ No se encontró ningún CSV en {directorio}.")

# ——— Ejecución como script ———
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <índice 0–4>")
    else:
        main(sys.argv[1])
