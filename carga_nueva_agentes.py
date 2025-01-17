import pandas as pd
import mysql.connector

# Lee el archivo Excel
df_excel = pd.read_excel(r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\Layout_Carga_Ejecutivo Julio.xlsx')

# Imprime las columnas del DataFrame de Excel
print("Columnas en df_excel:", df_excel.columns)

# Configuración de la conexión a la base de datos
conn = mysql.connector.connect(
    host='192.168.51.210',
    user='root',
    password='',
    database='audios_dana'
)

cursor = conn.cursor(dictionary=True)

# Cargar la tabla MySQL en un DataFrame
cursor.execute("SELECT * FROM tabla_historico_asignaciones")
rows = cursor.fetchall()
df_mysql = pd.DataFrame(rows)

# Imprime las columnas del DataFrame de MySQL
print("Columnas en df_mysql:", df_mysql.columns)

# Asegúrate de que las columnas coincidan con los nombres correctos
excel_agent_id_col = 'AgentId'
mysql_agent_id_col = 'agentId'

# Verificar que las columnas existen en los DataFrames
if excel_agent_id_col not in df_excel.columns:
    raise KeyError(f"Columna '{excel_agent_id_col}' no encontrada en el DataFrame de Excel")

if mysql_agent_id_col not in df_mysql.columns:
    raise KeyError(f"Columna '{mysql_agent_id_col}' no encontrada en el DataFrame de MySQL")

# Identificar agentes comunes
common_agents = df_excel[df_excel[excel_agent_id_col].isin(df_mysql[mysql_agent_id_col])]

# Identificar nuevos agentes y preparar datos para insertar
new_agents = df_excel[~df_excel[excel_agent_id_col].isin(df_mysql[mysql_agent_id_col])]
new_agents = new_agents.assign(Lunes=0, Martes=0, Miercoles=0, Jueves=0, Viernes=0, Sabado=0, Domingo=0, RegstrosAsignados=3)

# Identificar agentes obsoletos
obsolete_agents = df_mysql[~df_mysql[mysql_agent_id_col].isin(df_excel[excel_agent_id_col])]

# Insertar nuevos agentes en la base de datos
for index, row in new_agents.iterrows():
    cursor.execute("""
        INSERT INTO tabla_historico_asignaciones (No_Empleado, region, antiguedad, agentId, Lunes, Martes, Miercoles, Jueves, Viernes, Sabado, Domingo, RegstrosAsignados)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (row['No Emp'], row['Region_Emp'], row['Antiguedad'], row[excel_agent_id_col], 0, 0, 0, 0, 0, 0, 0, 3))

conn.commit()

# Eliminar agentes obsoletos de la base de datos
for agent_id in obsolete_agents[mysql_agent_id_col]:
    cursor.execute("DELETE FROM tabla_historico_asignaciones WHERE agentId = %s", (agent_id,))

conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()
