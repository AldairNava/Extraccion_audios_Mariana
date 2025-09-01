import os
import shutil

def delete_contents(folder_paths):
    for folder_path in folder_paths:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
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
        r'C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_retenciones',
        r'C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios',
        r'C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios_apo',
        r'C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte',
        r'C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte_apo',
        r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_televentas",
        r"C:\Extraccion_Mariana_Continuo\audios_subidos"
    ]

    delete_contents(folders_to_clear)