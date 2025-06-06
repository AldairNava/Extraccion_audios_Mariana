import sys
import os
import pandas as pd
import mysql.connector
import threading
from send2trash import send2trash

def find_csv_file(directory):
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            return os.path.join(directory, file)
    return None

def load_data_to_db(file_path, table_name):
    if not file_path:
        print("No se encontró ningún archivo .csv en el directorio especificado.")
        return
    
    df = pd.read_csv(file_path)
    
    # Seleccionar las columnas necesarias como en el primer script
    columns_to_keep = ["External ID", "Interaction Time", "Duration", "Metadata: agentId", 
                       "Metadata: Cuenta", "Metadata: CasoNegocio"]
    df = df[columns_to_keep]

    # Renombrar las columnas para coincidir con los nombres de la base de datos
    df.columns = ["External_ID", "Interaction_Time", "Duration", "Metadata_agentId", "Metadata_Cuenta", "Metadata_CasoNegocio"]

    # Aquí configuramos el temporizador de 90 segundos
    def timeout():
        print("No es posible establecer conexión a la base de datos. El tiempo de espera fue mayor a 90 segundos.")
        sys.exit()

    timer = threading.Timer(90.0, timeout)
    timer.start()

    try:
        connection = mysql.connector.connect(
            host="192.168.51.210",
            user="root",
            password="",
            database="audios_dana",
            connection_timeout=90  # Establece un tiempo de espera de 90 segundos
        )
        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (External_ID, Interaction_Time, Duration, Metadata_agentId, Metadata_Cuenta, Metadata_CasoNegocio)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        inserted_rows_count = 0  # Inicializar el contador
        failed_rows_count = 0  # Contador de registros fallidos

        print("tabla definida e insertando registros...")
        for _, row in df.iterrows():
            try:
                cursor.execute(insert_query, tuple(row))
                inserted_rows_count += 1
            except mysql.connector.Error as err:
                # print(f"Error al insertar el registro: {row}. Error: {err}")
                failed_rows_count += 1

        connection.commit()

        cursor.close()
        connection.close()

        print(f"Se insertaron {inserted_rows_count} registros en la tabla {table_name}.")
        print(f"Fallaron {failed_rows_count} registros durante la inserción.")
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
    finally:
        timer.cancel()

    try:
        print("mandando a papeleria archivo")
        send2trash(file_path)
        print(f"Archivo {file_path} eliminado exitosamente.")
    except Exception as e:
        print(f"Error al eliminar el archivo {file_path}: {str(e)}")

def main(i):
    directories = [
        r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_rar",
        r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_rar",
        r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\retenciones_rar",
        r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_apodaca_rar",
        r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_apodaca_rar"
    ]
    
    table_names = [
        "reporte_audios_servicios",
        "reporte_audios_soporte",
        "reporte_audios_retenciones",
        "reporte_audios_servicios_apodaca",
        "reporte_audios_soporte_apodaca"
    ]
    
    if 0 <= int(i) < len(directories):
        print("buscando archivo")
        directory = directories[int(i)]
        file_path = find_csv_file(directory)
        if file_path:
            print("archivo encontrado subiendo registros...")
            load_data_to_db(file_path, table_names[int(i)])
        else:
            print(f"No se encontró ningún archivo .csv en el directorio {directory}.")
    else:
        print("Valor de i no válido. Debe estar entre 0 y 4.")

if __name__ == "__main__":
    manaul=False
    if manaul==True:
        i=2
        main(i)
    else:
        if len(sys.argv) > 1:
            i = sys.argv[1]
            main(i)
        else:
            print("Por favor, proporciona el nombre del archivo como argumento de línea de comandos.")
