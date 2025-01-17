import os

# Ruta de la carpeta donde se guardarán los archivos
carpeta_destino = r'C:\Users\Jotzi1\Desktop\Proceso_Clidad_1\transcripciones'

# Crear la carpeta si no existe
os.makedirs(carpeta_destino, exist_ok=True)

# Leer la lista de nombres desde un archivo .txt
with open(r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\lista.txt', 'r') as archivo:
    nombres = archivo.readlines()

# Crear un archivo .txt para cada nombre en la lista dentro de la carpeta especificada
for nombre in nombres:
    nombre = nombre.strip()  # Eliminar espacios en blanco y saltos de línea
    if nombre:  # Verificar que el nombre no esté vacío
        with open(os.path.join(carpeta_destino, f'{nombre}.txt'), 'w') as nuevo_archivo:
            nuevo_archivo.write(f'Este archivo es para: {nombre}')
