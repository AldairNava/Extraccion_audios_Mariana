import os
import shutil
from send2trash import send2trash

def delete_contents(folder_paths):
    for folder_path in folder_paths:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if file_path.endswith('.csv'):
                            send2trash(file_path)
                            print(f"Archivo CSV movido a la papelera: '{file_path}'")
                        else:
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Error al eliminar '{file_path}': {e}")

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                    except Exception as e:
                        print(f"Error al eliminar '{dir_path}': {e}")

            print(f"Contenido de '{folder_path}' eliminado correctamente.")
        else:
            print(f"No se encontró el directorio '{folder_path}'.")

if __name__ == "__main__":
    folders_to_clear = [
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_rar',
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\retenciones_rar',
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_apodaca_rar',
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_apodaca_rar',
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_rar',
        r'C:\Extraccion_Mariana_Continuo\archivos_rar\televentas_rar'
    ]

    delete_contents(folders_to_clear)
