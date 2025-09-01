import mysql.connector
import os
from datetime import datetime, timedelta

# Configuración de la base de datos
db_config = {
    'host': '192.168.51.210',
    'user': 'root',
    'password': 'thor',
    'database': 'audios_dana'
}

def obtener_nombres_audios_sin_extension():
    conexion = mysql.connector.connect(**db_config)
    try:
        print("Seleccionando audios..")
        cursor = conexion.cursor()
        
        # Fecha de hace 7 días y la fecha de hoy
        hace_siete_dias = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # Consulta para obtener los nombres de los audios
        query = f"""
            SELECT audio_name 
            FROM audios 
            WHERE DATE(fecha_llamada) BETWEEN '{hace_siete_dias}' AND '{hoy}';
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Eliminar la extensión .mp3 de cada nombre de audio
        nombres_sin_extension = [os.path.splitext(fila[0])[0] for fila in resultados]
        cursor.close()
        
        return nombres_sin_extension
    finally:
        conexion.close()

def eliminar_audios_de_tablas(nombres_audios):
    conexion = mysql.connector.connect(**db_config)
    try:
        print("eliminando audios")
        cursor = conexion.cursor()
        
        # Tablas en las que se realizará la eliminación
        tablas = [
            'reporte_audios_servicios',
            'reporte_audios_soporte',
            'reporte_audios_retenciones',
            'reporte_audios_servicios_apodaca',
            'reporte_audios_soporte_apodaca'
        ]
        
        for nombre_audio in nombres_audios:
            for tabla in tablas:
                print(f"audios duplicados eliminados de {tabla}")
                query = f"DELETE FROM {tabla} WHERE External_ID = %s"
                cursor.execute(query, (nombre_audio,))
                
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()

if __name__ == "__main__":
    try:
        nombres_audios_sin_extension = obtener_nombres_audios_sin_extension()
        eliminar_audios_de_tablas(nombres_audios_sin_extension)
        print("Audios eliminados correctamente de las tablas.")
    except Exception as e:
        print(f"Error en el proceso: {e}")
