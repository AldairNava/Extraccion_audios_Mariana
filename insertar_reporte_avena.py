import mysql.connector

# Configurar la conexión a la base de datos
config = {
    "host":"192.168.51.210",
    "user":"root",
    "password":"",
    "database":"marianaavena"
}

try:
    # Establecer conexión
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Definir la consulta SQL
    query = """
    INSERT INTO marianaavena.reporte_audios_retenciones
    SELECT * FROM audios_dana.reporte_audios_retenciones;
    """

    # Ejecutar la consulta
    cursor.execute(query)
    conn.commit()

    print("Registros copiados exitosamente.")

except mysql.connector.Error as e:
    print(f"Error: {e}")

finally:
    # Cerrar la conexión
    if conn.is_connected():
        cursor.close()
        conn.close()
