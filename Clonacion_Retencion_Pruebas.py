import mysql.connector
from datetime import datetime, timedelta
from Tele import send_msg

def transferir_audios():
    conexion = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="",
        database="audios_dana_pruebas"
    )
    cursor = conexion.cursor()

    ayer = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

    query_select = f"""
    SELECT 
        audio_name, audio_path, created_at, modified_at, fecha_llamada,
        played, analyzed, status, owner, deleted, groserias, masivo,
        problematica, solucion, tipo, guia, agente, supervisor, id_zona,
        idAsesor, nomAsesor, AHT, id_analista, tarea_programada,
        analizado_tareas, revisado_analista, ip
    FROM audios_dana.audios
    WHERE guia = 'guia_set_12' 
      AND status = 'Transcrito' 
      AND DATE(fecha_llamada) = '{ayer}'
    """
    cursor.execute(query_select)
    resultados = cursor.fetchall()

    print(f"Se encontraron {len(resultados)} registros para procesar.")
    
    registros_actualizados = 0
    registros_insertados = 0

    for fila in resultados:
        # Verificar existencia en la base de pruebas
        query_check = """
        SELECT COUNT(*) 
        FROM audios_dana_pruebas.audios
        WHERE audio_name = %s
        """
        cursor.execute(query_check, (fila[0],))
        existe = cursor.fetchone()[0]

        if existe:
            query_update = """
            UPDATE audios_dana_pruebas.audios
            SET status = %s
            WHERE audio_name = %s
            """
            cursor.execute(query_update, (fila[7], fila[0]))
            registros_actualizados += 1
            print(f"Registro actualizado: {fila[0]} (status: {fila[7]})")
        else:
            query_insert = """
            INSERT INTO audios_dana_pruebas.audios (
                audio_name, audio_path, created_at, modified_at, fecha_llamada,
                played, analyzed, status, owner, deleted, groserias, masivo,
                problematica, solucion, tipo, guia, agente, supervisor, id_zona,
                idAsesor, nomAsesor, AHT, id_analista, tarea_programada,
                analizado_tareas, revisado_analista, ip
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, fila)
            registros_insertados += 1
            print(f"Registro insertado: {fila[0]}")

    conexion.commit()

    msg = (f"Proceso completado. Registros actualizados: {registros_actualizados}. "
           f"Registros insertados: {registros_insertados}.")
    print(msg)
    send_msg(msg)

    cursor.close()
    conexion.close()
