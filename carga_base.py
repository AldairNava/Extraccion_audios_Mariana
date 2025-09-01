import sys
import os
import pandas as pd
import mysql.connector
import threading
from send2trash import send2trash

audios_config = {
    "host": "192.168.51.210",
    "user": "root",
    "password": "thor",
    "database": "audios_dana"
}

mariana_config = {
    "host": "192.168.51.210",
    "user": "root",
    "password": "thor",
    "database": "marianaavena"
}

AUDIO_FOLDERS = [
    r"carpeta_de_audios/audios_filtrados",
    r"carpeta_de_audios/audios_rar_retenciones",
    r"carpeta_de_audios/audios_rar_servicios",
    r"carpeta_de_audios/audios_rar_servicios_apo",
    r"carpeta_de_audios/audios_rar_soporte",
    r"carpeta_de_audios/audios_rar_soporte_apo",
    r"carpeta_de_audios/audios_rar_televentas"
]
BASE_AUDIO_PATH = r"C:\Extraccion_Mariana_Continuo"

def find_csv_file(directory):
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            return os.path.join(directory, file)
    return None

def buscar_audio(external_id):
    for carpeta in AUDIO_FOLDERS:
        ruta = os.path.join(BASE_AUDIO_PATH, carpeta, f"{external_id}.mp3")
        if os.path.isfile(ruta):
            return ruta
    return None

def audio_valido(external_id):
    ruta_audio = buscar_audio(external_id)
    return bool(ruta_audio and os.path.getsize(ruta_audio) >= 5 * 1024)

def asegurar_columnas(df, columnas_objetivo):
    """
    Asegura que todas las columnas objetivo existen en el DataFrame.
    Si alguna falta, la agrega con None.
    """
    for col in columnas_objetivo:
        if col not in df.columns:
            df[col] = None
    return df

def load_data_to_db(file_path, table_name):
    if not file_path:
        print("No se encontró ningún archivo .csv en el directorio especificado.")
        return
    
    columns_to_keep = ["External ID", "Interaction Time", "Duration", "Metadata: agentId", 
                       "Metadata: Cuenta", "Metadata: CasoNegocio"]
    # Aseguramos que todas las columnas existan
    df = pd.read_csv(file_path)
    df = asegurar_columnas(df, columns_to_keep)
    df = df[columns_to_keep]

    df.columns = ["External_ID", "Interaction_Time", "Duration", "Metadata_agentId", "Metadata_Cuenta", "Metadata_CasoNegocio"]

    registros_validos = []
    omitidos = 0
    for _, row in df.iterrows():
        external_id = str(row["External_ID"])
        if audio_valido(external_id):
            valores = []
            for v in row:
                if pd.isna(v):
                    valores.append(None)
                else:
                    valores.append(v)
            registros_validos.append(tuple(valores))
        else:
            omitidos += 1

    def timeout():
        print("No es posible establecer conexión a la base de datos. El tiempo de espera fue mayor a 90 segundos.")
        sys.exit()

    timer = threading.Timer(90.0, timeout)
    timer.start()

    try:
        connection = mysql.connector.connect(
            host="192.168.51.210",
            user="root",
            password="thor",
            database="audios_dana",
            connection_timeout=90
        )
        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (External_ID, Interaction_Time, Duration, Metadata_agentId, Metadata_Cuenta, Metadata_CasoNegocio)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        inserted_rows_count = 0
        failed_rows_count = 0

        print("tabla definida e insertando registros...")
        for row in registros_validos:
            try:
                cursor.execute(insert_query, row)
                inserted_rows_count += 1
            except mysql.connector.Error as err:
                print(f"Error al insertar el registro: {row}. Error: {err}")
                failed_rows_count += 1

        connection.commit()

        cursor.close()
        connection.close()

        print(f"Se insertaron {inserted_rows_count} registros en la tabla {table_name}.")
        print(f"Fallaron {failed_rows_count} registros durante la inserción.")
        print(f"Se omitieron {omitidos} registros por audio no encontrado o menor a 5KB.")
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
    finally:
        timer.cancel()

def load_data_to_mariana(file_path, table_name, config):
    cols = ["External ID", "Interaction Time", "Duration", "Metadata: agentId",
            "Metadata: Cuenta", "Metadata: CasoNegocio"]
    df = pd.read_csv(file_path)
    df = asegurar_columnas(df, cols)
    df = df[cols]
    df.columns = ["External_ID", "Interaction_Time", "Duration",
                  "Metadata_agentId", "Metadata_Cuenta", "Metadata_CasoNegocio"]

    registros_validos = []
    for _, row in df.iterrows():
        ext = str(row["External_ID"])
        if audio_valido(ext):
            registros_validos.append(tuple(None if pd.isna(v) else v for v in row))

    conn2 = mysql.connector.connect(**config, connection_timeout=90)
    cur2 = conn2.cursor()
    insert_sql = f"""
        INSERT INTO {table_name}
        (External_ID, Interaction_Time, Duration, Metadata_agentId, Metadata_Cuenta, Metadata_CasoNegocio)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    inserted = 0
    for vals in registros_validos:
        try:
            cur2.execute(insert_sql, vals)
            inserted += 1
        except mysql.connector.Error as e:
            print(f"[marianaavena] Error inserción {vals}: {e}")
    conn2.commit()
    cur2.close()
    conn2.close()
    print(f"Se insertaron {inserted} registros en marianaavena.{table_name}.")

speech_table_map = {
    "reporte_audios_servicios":         "reporteAudiosServiciosSpeech",
    "reporte_audios_soporte":           "reporteAudiosSoporteSpeech",
    "reporte_audios_retenciones":       "reporteAudiosRetencionesSpeech",
    "reporte_audios_televentas":        "reporteAudiosteleventasSpeech",
    "reporte_audios_servicios_apodaca": "reporteAudiosServiciosApodacaSpeech",
    "reporte_audios_soporte_apodaca":   "reporteAudiosSoporteApodacaSpeech"
}

def main(i):
    directories = [
        r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_rar",
        r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_rar",
        r"C:\Extraccion_Mariana_Continuo\archivos_rar\retenciones_rar",
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\televentas_rar',
        r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_apodaca_rar",
        r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_apodaca_rar"
    ]
    table_names = [
        "reporte_audios_servicios",
        "reporte_audios_soporte",
        "reporte_audios_retenciones",
        "reporte_audios_televentas",
        "reporte_audios_servicios_apodaca",
        "reporte_audios_soporte_apodaca"
    ]

    idx = int(i)
    if not (0 <= idx < len(directories)):
        print("Valor de i no válido. Debe estar entre 0 y 5.")
        return

    directory = directories[idx]
    file_path = find_csv_file(directory)
    if not file_path:
        print(f"No se encontró CSV en {directory}.")
        return

    tabla_orig   = table_names[idx]
    tabla_speech = speech_table_map[tabla_orig]

    print(f"--> Archivo: {file_path}")
    print(f"--> Cargando en {tabla_orig} y {tabla_speech}…")
    load_data_to_db(file_path, tabla_orig)
    load_data_to_db(file_path, tabla_speech)

    if idx == 2:
        print("--> Adicional: cargando en marianaavena.reporte_audios_retenciones …")
        load_data_to_mariana(file_path,
                             "reporte_audios_retenciones",
                             mariana_config)

    send2trash(file_path)
    print(f"Archivo {file_path} movido a la papelera.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Por favor, proporciona el índice (0–5) como argumento.")
