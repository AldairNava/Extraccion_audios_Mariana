import os
import shutil
import patoolib
import patoolib.util
import sys
import zipfile

def limpiar_carpeta(carpeta):
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        try:
            if os.path.isfile(ruta) or os.path.islink(ruta):
                os.unlink(ruta)
            elif os.path.isdir(ruta):
                shutil.rmtree(ruta)
        except Exception as e:
            print(f'Error al eliminar {ruta}. Razón: {e}')

def archivos_mp3_zip(ruta_zip):
    """Devuelve la lista de archivos .mp3 que hay dentro del ZIP."""
    archivos = []
    try:
        with zipfile.ZipFile(ruta_zip, 'r') as zf:
            archivos = [info.filename for info in zf.infolist()
                        if info.filename.lower().endswith('.mp3')]
    except Exception as e:
        print(f"Error leyendo {ruta_zip} para listar archivos mp3: {e}")
    return archivos

def mover_y_extraer(nombre_prefijo, carpeta_destino, contrasenas):
    carpeta_descargas = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    for archivo in os.listdir(carpeta_descargas):
        if nombre_prefijo in archivo and archivo.lower().endswith('.zip'):
            origen = os.path.join(carpeta_descargas, archivo)
            destino = os.path.join(carpeta_destino, archivo)
            print(f"Moviendo archivo {archivo} a {destino}...")
            shutil.move(origen, destino)

            # Obtener lista de mp3 esperados en el zip
            mp3_esperados = archivos_mp3_zip(destino)

            # Intentar extracción con cada contraseña
            extrajo = False
            for pwd in contrasenas:
                try:
                    print(f"Extrayendo {archivo} en {carpeta_destino} con contraseña '{pwd}'…")
                    patoolib.extract_archive(destino,
                                             outdir=carpeta_destino,
                                             password=pwd)
                    extrajo = True
                    break
                except patoolib.util.PatoolError as e:
                    print(f"  ⚠️ Error extrayendo con '{pwd}': {e}")
            if not extrajo:
                print("  ❌ No se pudo extraer completamente con ninguna contraseña.")

            # 1) Eliminar carpetas vacías y contar cuántas se eliminan
            eliminadas = 0
            for entry in os.listdir(carpeta_destino):
                ruta_entry = os.path.join(carpeta_destino, entry)
                if os.path.isdir(ruta_entry):
                    mp3s = [f for f in os.listdir(ruta_entry)
                            if f.lower().endswith('.mp3')]
                    if not mp3s:
                        shutil.rmtree(ruta_entry)
                        eliminadas += 1
            print(f"✅ Se eliminaron {eliminadas} carpetas vacías en '{carpeta_destino}'.")

            # 2) Contar archivos .mp3 extraídos realmente
            mp3_extraidos = []
            for root, _, files in os.walk(carpeta_destino):
                for f in files:
                    if f.lower().endswith('.mp3'):
                        rel_path = os.path.relpath(os.path.join(root, f), carpeta_destino)
                        mp3_extraidos.append(rel_path.replace("\\", "/"))
            print(f"✅ Se extrajeron {len(mp3_extraidos)} archivos .mp3 de '{nombre_prefijo}' en '{carpeta_destino}'.")

            # 3) Mostrar archivos faltantes
            faltantes = [x for x in mp3_esperados if not any(os.path.basename(x) == os.path.basename(y) for y in mp3_extraidos)]
            if faltantes:
                print("\n❌ Los siguientes archivos .mp3 NO se extrajeron (probable contraseña incorrecta o daño):")
                for f in faltantes:
                    print(f"- {f}")
            else:
                print("\nTodos los archivos .mp3 del ZIP se extrajeron correctamente.")

            return

    print(f"No se encontró ningún ZIP con prefijo '{nombre_prefijo}' en Descargas.")

def main(i):
    carpetas = {
        '0': r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_rar",
        '1': r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_rar",
        '2': r"C:\Extraccion_Mariana_Continuo\archivos_rar\retenciones_rar",
        '3': r"C:\Extraccion_Mariana_Continuo\archivos_rar\televentas_rar",
        '4': r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_apodaca_rar",
        '5': r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_apodaca_rar"
    }
    contrasenas = ['Cyb*^1234567']

    carpeta_destino = carpetas.get(i)
    if not carpeta_destino:
        print(f"El valor '{i}' no es válido. Usa un número entre 0 y 5.")
        return

    nombre_prefijo = 'p-efgarciac' if i in ('0', '1', '2') else 'p-cmanriquez'
    mover_y_extraer(nombre_prefijo, carpeta_destino, contrasenas)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Por favor, proporciona un índice (0–5) como argumento de línea de comandos.")
