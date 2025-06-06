import mysql.connector
from datetime import datetime, timedelta

config = {
    'host': '192.168.51.210',
    'user': 'root',
    'password': '',
    'database': 'marianaavena'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    fecha_limite = datetime.now() - timedelta(days=3)
    tres_dias_atras = fecha_limite.strftime('%Y-%m-%d %H:%M:%S')

    guias = ['guia_set_1', 'guia_set_9', 'guia_set_10', 'guia_set_11', 'guia_set_12']

    for guia in guias:
        print(f"Consultando audios para {guia}")
        consulta = f"SELECT audio_name FROM audios WHERE date(fecha_llamada) >= '{tres_dias_atras}' AND guia = '{guia}'"
        cursor.execute(consulta)
        filenames = cursor.fetchall()
        print(f"Encontrados {len(filenames)} audios en {guia}")

        tablas_a_eliminar = [f'calificaciones_{g}' for g in guias if g != guia]

        for filename in filenames:
            for tabla in tablas_a_eliminar:
                print(f"Eliminando {filename[0]} de {tabla}")
                eliminar = f"DELETE FROM {tabla} WHERE filename = %s"
                cursor.execute(eliminar, (filename[0],))

    conn.commit()

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

print("Los audios y las entradas correspondientes han sido eliminados.")
