from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import datetime
import random
import pandas as pd
import sys
import pyautogui
from Tele import send_msg
import subprocess
import time
import logging
import os
from utileria.utileria_genesys import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
logging.getLogger("tensorflow").setLevel(logging.ERROR)

def find_zip_p_efgarciac(directory):
    """
    Busca el primer archivo .zip en 'directory' cuyo nombre comience con 'p-efgarciac'.
    Devuelve True si lo encuentra, False en caso contrario.
    """
    prefijo = "p-efgarciac"
    for nombre in os.listdir(directory):
        base, ext = os.path.splitext(nombre)

        if ext.lower() == ".zip" and base.startswith(prefijo):
            print("Zip encontrado:", nombre)
            return False
    
    print("Zip No Encontrado")
    time.sleep(90)
    return True


pyautogui.FAILSAFE = False

def validar_elemento_presentes(driver, i, x, manual,x_path, intentos_fallidos):
    intentos = 0
    MAX_INTENTOS = 5

    while intentos < MAX_INTENTOS:
        try:
            buscar = driver.find_element(By.XPATH, x_path)
            print("Elemento encontrado y está presente.")
            break

        except Exception as e:
            intentos += 1
            print("Cargando Ventana")
            print(f"Intento {intentos} fallido. Error: 'elemento no Enocntrado'")
            time.sleep(30)
    
    if intentos == MAX_INTENTOS:
        print(f"No se pudo encontrar el elemento después de {MAX_INTENTOS} intentos. Reiniciando el proceso.")
        driver.quit()
        main(i, x, manual, intentos_fallidos) 

def descargas_automatica_no_seguro(driver):
    print("\nIniciando ajuste descargas automáticas")

    for _ in range(7):
        element = driver.switch_to.active_element
        element.send_keys(Keys.TAB)
        sleep(1)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    element.send_keys(Keys.DOWN)
    sleep(2)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    print("\nIniciando ajuste descargas no seguras")
    
    for _ in range(5):
        element = driver.switch_to.active_element
        element.send_keys(Keys.TAB)
        sleep(1)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    element.send_keys(Keys.DOWN)
    sleep(2)
    
    element.send_keys(Keys.ENTER)
    sleep(2)


def obtener_vqd(i):
    archivos_excel = {
        "Listado de VQDs Servicios": r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_vqd\Listado de VQDs Servicios.xlsx',
        "Listado de VQDs Soporte": r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_vqd\Listado de VQDs Soporte.xlsx',
        "Listado de VQDs Retencion": r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_vqd\Listado de VQDs Retencion.xlsx'
    }

    archivo_excel = archivos_excel[list(archivos_excel.keys())[i]]

    datos = pd.read_excel(archivo_excel)

    VQDs = []
    for index, row in datos.iterrows():
        if 2 <= index + 1 <= 29:
            VQDs.append(row[3])

    if len(VQDs) > 5:
        VQDs = random.sample(VQDs, 5)

    print("\nValores de VQD:")
    for VQD in VQDs:
        print(VQD)

    conteo_total_vqd = len(VQDs)
    print("\nConteo total de valores en VQD:", conteo_total_vqd)

    return VQDs


def agregar_valores_vqd(driver, i):
    valores_input = driver.find_element(By.XPATH, metadatos_valores_input)
    driver.execute_script("arguments[0].scrollIntoView(true);", valores_input)
    VQDs = obtener_vqd(i)
    valores_input.click()
    valores_input.send_keys(VQDs[0])
    sleep(2)
    valores_input_but_mas = driver.find_element(By.XPATH, metadatos_valores_boton_mas)
    driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_but_mas)
    valores_input_but_mas.click()
    
    for j, vqd in enumerate(VQDs[1:], start=2):
        valores_input_mas = driver.find_element(By.XPATH, f'/html/body/div[1]/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[2]/div[3]/div[1]/div/metadata-filter/div/div/div/div/div[{j}]/div[2]/input[1]')
        driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_mas)
        valores_input_mas.click()
        valores_input_mas.send_keys(vqd)
        sleep(2)
        if j < len(VQDs):
            valores_input_but_mas = driver.find_element(By.XPATH, f'/html/body/div[1]/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[2]/div[3]/div[1]/div/metadata-filter/div/div/div/div/div[{j}]/div[3]')
            driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_but_mas)
            valores_input_but_mas.click()

def main(i, x,manual, intentos_fallidos):

    iteraccion = (x, i,)
    intentos_actuales = intentos_fallidos.get(iteraccion, 0)
    try:
        opciones = webdriver.ChromeOptions()
        opciones.add_argument('--ignore-certificate-errors') 
        opciones.add_experimental_option("excludeSwitches", ['enable-automation']) 
        # opciones.add_argument("--headless")  
        opciones.add_argument("--disable-extensions")  
        opciones.add_argument("--disable-gpu")  
        opciones.add_argument("--no-sandbox")  
        opciones.add_argument("--log-level=3")  
        opciones.add_argument("--ignore-certificate-errors")  
        opciones.add_argument("--disable-software-rasterizer")  
        opciones.add_argument("--disable-logging") 
        driver = webdriver.Chrome(options=opciones)

        driver.maximize_window()

        # Ajuste para descarga de audios sin permisos
        url_ajuste = 'chrome://settings/content/siteDetails?site=http%3A%2F%2F10.90.30.75'
        driver.get(url_ajuste)
        
        sleep(5)
        
        descargas_automatica_no_seguro(driver)
        sleep(5)

        url = 'https://10.90.30.75/speechminer/pages/login/login.aspx'

        driver.get(url)
        sleep(5)

        #validar carga de pagina en chrome
        validar_elemento_presentes(driver, i, x, manual,check_gen, intentos_fallidos)

        # ************ Inicio de sesion
        print("Seleccionando opcion Genesys")
        boton_genesys = driver.find_element(By.XPATH, check_gen)
        boton_genesys.click()
        sleep(1)

        print("Ingresando usuario")
        user = driver.find_element(By.XPATH, usuario)
        user.click()
        user.send_keys('p-efgarciac')
        sleep(1)

        print("Ingresando contraseña")
        password = driver.find_element(By.XPATH, contraseña)
        password.click()
        password.send_keys('14080')
        sleep(1)

        print("Iniciando sesión")
        password.send_keys(Keys.RETURN)
            
        validar_elemento_presentes(driver, i, x, manual,'//span[@class = "navbar-appname ng-binding"]', intentos_fallidos)
        
        # ********** SELECCION DE RANGO DE FECHAS
        print("\nSeleccionando rango de fechas de seleccion de descarga")
        rango = driver.find_element(By.XPATH, rango_de_fechas)
        rango.click()
        sleep(2)

        print("Seleccionando opcion Personalizada")
        personal = driver.find_element(By.XPATH, personalizado)
        driver.execute_script("arguments[0].scrollIntoView(true);", personal)
        personal.click()
        sleep(2)

        if manual == True:
            print("Ingresando a rango de fecha De: ")
            de_rango = driver.find_element(By.XPATH, de)
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=1)
            fecha_formateada = yesterday.strftime("%m/%d/%y")
            print(fecha_formateada)
            de_rango.click()
            de_rango.send_keys(fecha_formateada)
            sleep(2)
        else:
            print("Ingresando a rango de fecha De: ")
            de_rango = driver.find_element(By.XPATH, de)
            today = datetime.datetime.now()
            fecha_formateada = today.strftime("%m/%d/%y")
            print(fecha_formateada)
            de_rango.click()
            de_rango.send_keys(fecha_formateada)
            sleep(2)

        # SELECCION DE PRIMER HORARIO POR HORA DE EJECUCION
        def seleccionar_horario(driver, x, fecha_1, xpath):

            if x == "1":
                rango_hora_2 = driver.find_element(By.XPATH, fecha_1)
                rango_hora_2.click()
                print("x es 0: No se selecciona ningún horario, se continúa con lo demás.")
                sleep(2)
                return

            if x in xpath:
                print(f"Seleccionando horario final a hora {xpath[x]['hora']}")
                rango_hora_2 = driver.find_element(By.XPATH, fecha_1)
                rango_hora_2.click()
                sleep(2)

                elemento = driver.find_element(By.XPATH, xpath[x]['xpath'])
                driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                elemento.click()
                sleep(2)
            else:
                print("Valor de x no válido. Proporcione un valor entre 0 y 10.")
        
        xpath = {
            "2": {"hora": "2:00 pm", "xpath": dos_pm_1},
            "3": {"hora": "6:00 pm", "xpath": seis_pm_1}
        }
        seleccionar_horario(driver, x, fecha_1, xpath)

        if manual == True:
            print("Ingresando a rango de fecha De: ")
            de_rango = driver.find_element(By.XPATH, a)
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=1)
            fecha_formateada = yesterday.strftime("%m/%d/%y")
            print(fecha_formateada)
            de_rango.click()
            de_rango.send_keys(fecha_formateada)
            sleep(2)
        else:
            print("Ingresando a rango de fecha De: ")
            de_rango = driver.find_element(By.XPATH, a)
            today = datetime.datetime.now()
            fecha_formateada = today.strftime("%m/%d/%y")
            print(fecha_formateada)
            de_rango.click()
            de_rango.send_keys(fecha_formateada)
            sleep(2)
            
        
        # SELECCION DE SEGUNDO HORARIO POR HORA DE EJECUCION
        def seleccionar_horario_final(driver, x, hora_a, xpath):
            if x in xpath:
                print(f"Seleccionando horario final a hora {xpath[x]['hora']}")
                rango_hora_2 = driver.find_element(By.XPATH, hora_a)
                rango_hora_2.click()
                sleep(2)

                elemento = driver.find_element(By.XPATH, xpath[x]['xpath'])
                driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                elemento.click()
                sleep(2)
            else:
                print("Valor de x no válido. Proporcione un valor entre 0 y 10.")
        
        xpath = {
            "1": {"hora": "10:00 am", "xpath": diez_am_2},
            "2": {"hora": "5:00 pm", "xpath": cinco_pm_2},
            "3": {"hora": "11:00 pm", "xpath": once_pm_2},
        }
        seleccionar_horario_final(driver, x, hora_a, xpath)
                    

        # ********** SELECCION DE RANGO DE Habitantes

        print("\nSeleccionando hablantes")
        hablante = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/button')
        hablante.click()
        sleep(2)
        
        sleep(10)
        check_hablantes = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/div/tree-view/div/div[2]/div/span[1]')
        check_hablantes.click()
        sleep(2)
        
        hablante_2 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/button')
        hablante_2.click()
        sleep(2)
        
        print("\nIngresando a Metadatos")
        nombre = driver.find_element(By.XPATH, nombres)
        nombre.click()

        observar = True
        while observar:
            try:
                observar_solamente = driver.find_element(By.XPATH, busqueda_meta)
                print("metadatos abierto")
                sleep(5)
                break
            except:
                print("Cargando pestaña de metadatos")
                sleep(5)

        print("Ingresando valor VQD")
        busqueda_VQD = driver.find_element(By.XPATH, busqueda)
        busqueda_VQD.click()
        busqueda_VQD.send_keys('VQD')
        sleep(2)

        checkbox_vqd = driver.find_element(By.XPATH, check_vqd_cdmx)
        checkbox_vqd.click()
        sleep(2)
        
        valor = driver.find_element(By.XPATH, valores)
        valor.click()
        sleep(2)
        
        agregar_valores_vqd(driver, i)
        sleep(2)
        
        print("Ingresando rango de tiempo de llamadas")
        duracion = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/dropdown-select/div/div/button')
        duracion.click()
        sleep(2)
        
        duracion_entre = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/dropdown-select/div/div/ul/li[3]')
        duracion_entre.click()
        sleep(2)
        
        rango_llamada_1 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/div/input[1]')
        rango_llamada_1.click()
        sleep(2)
        if x == '1':
            rango_llamada_1.send_keys('200')
        else:
            rango_llamada_1.send_keys('600')
        sleep(1)
        rango_llamada_2 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/div/input[2]')
        rango_llamada_2.click()
        sleep(1)
        if x=='1':
            rango_llamada_2.send_keys('600')
        else:
            rango_llamada_2.send_keys('1200')
        sleep(1)
        
        
        busqueda_ex = driver.find_element(By.XPATH, buscar_resultados)
        busqueda_ex.click()
        sleep(20)

        validar_elemento_presentes(driver, i, x, manual,'//span[@dir="ltr" and contains(@ng-show, "params.dataProvider.totalNumberOfResults") and contains(@class, "ng-binding")]', intentos_fallidos)
        
        # ********** VENTANA DE EXPORTACION
        validar_elemento_presentes(driver, i, x, manual,reconocimiento, intentos_fallidos)
        print("Pagina de exportacion abierta")
        sleep(2)
        
        try:
            print("Esperando a que el checkbox de 'Seleccionar todo' esté presente y sea clickeable")
            print("Click en checkbox seleccion todo")
            checkbox_select = driver.find_element(By.XPATH, check_seleccion)
            checkbox_select.click()
            sleep(2)
            
            print("Expandiendo menu de seleccion")
            exp_sel = driver.find_element(By.XPATH, expacion)
            exp_sel.click()
            sleep(2)
            
            print("Seleccionando exportar")
            expo_expo = driver.find_element(By.XPATH, expacion_exportar)
            expo_expo.click()
            sleep(20)
            
            # ********** VENTANA DE EXPORTACION MODAL 1
            
            print("\nAccediendo a ventana modal 1 seleccion de audios")

            try:
                print("Esperando a que la primer ventana modal esté visible")
                modal = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.export-modal.in'))
                )
                print("Modal está visible")
                sleep(2)
                
                try:
                    print("Esperando a que el radio button esté clickeable")
                    radio_button = WebDriverWait(driver, 120).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="radio"]/label[input[@type="radio" and @value="true" and @ng-value="true"]]'))
                    )
                    print("Radio button está clickeable")
                    radio_button.click()
                    print("Hicimos clic en el radio button")
                except Exception as e:
                    print("Radio button no está presente o no es clickeable. Continuando sin hacer clic en el radio button.")
                
                sleep(2)
                
                print("Esperando a que el checkbox esté clickeable")
                checkbox = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="checkbox"]/label[input[@type="checkbox" and @ng-model="exportData.exportWithAudio"]]'))
                )

                print("Checkbox está clickeable")

                checkbox.click()
                print("Hicimos clic en el checkbox")
                
                sleep(2)
                
                print("Esperando a que el botón de exportar esté presente y sea clickeable")
                boton_exportar = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@translate="Explore.BatchActions.Export.ExportButton"]'))
                )

                print("Botón de exportar está presente y es clickeable")

                boton_exportar.click()
                print("Se hizo clic en el botón de exportar")
                sleep(5)


            except Exception as e:
                print(f"Ocurrió un error: {e}")
                main(i, x, manual, intentos_fallidos)
                return
                
                
            # ********** VENTANA DE EXPORTACION MODAL 2
            
            print("\nAccediendo a ventana modal 2 generador de contraseñas")
            
            try:
                print("Esperando a que la segunda ventana modal esté visible")
                modal = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.in'))
                )
                print("Modal está visible")

                sleep(2)
                
                print("Esperando a que el campo de contraseña esté presente y sea interactuable")
                input_contraseña = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "password-input"))
                )

                print("Campo de contraseña está presente y es interactuable")

                input_contraseña.clear()

                texto_contraseña = "Cyb*^1234567"
                input_contraseña.send_keys(texto_contraseña)
                
                sleep(2)

                print("Esperando a que el botón 'Exportar' esté presente y sea clickeable")
                boton_exportar = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@ng-if="logic.isStrongPassword()"]'))
                )

                print("Botón 'Exportar' está presente y es clickeable")

                boton_exportar.click()
                print("Se hizo clic en el botón 'Exportar'")
                
                sleep(2)
                
            except Exception as e:
                print(f"Ocurrió un error: {e}")
                main(i, x, manual, intentos_fallidos)
                return
                
            
            # ********** VENTANA DE EXPORTACION MODAL 3
            
            print("\nAccediendo a ventana modal 3 confirmacion")
            
            try:
                print("Esperando a que la tercer ventana modal esté visible")
                modal = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.in'))
                )
                print("Modal está visible")

                sleep(20)
            except Exception as e:
                print(f"Ocurrió un error: {e}")
                main(i, x, manual, intentos_fallidos)
                return
                
            try:
                print("Esperando a que el botón 'Completado' esté presente y sea clickeable")
                boton_completado = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@translate="General.Done"]'))
                )

                print("Botón 'Completado' está presente y es clickeable")

                boton_completado.click()
                print("Se hizo clic en el botón 'Completado'")
                sleep(3)
            except Exception as e:
                print(f"boton completado error: {e}")
                    
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Hora Actual:{hora_actual}")
            print("Esperando la descarga.......")
            sleep(400)

            directorio = r"C:\Users\Jotzi1\Downloads"
            resultado = find_zip_p_efgarciac(directorio)
            contador = 0  # Inicializa el contador

            while resultado and contador < 30:
                print("Buscando...")
                resultado = find_zip_p_efgarciac(directorio)
                contador += 1

            if contador == 30:
                print(f"Finalizado después de 30 intentos no se logro descargar el archivo del horario {x} campaña {i}.")
            else:
                print("Descarga exitosa Procediendo a extraer")

                
            try:
                usu_cierre = driver.find_element(By.XPATH, user_cierre)
                usu_cierre.click()
                sleep(3)

                cierre_final = driver.find_element(By.XPATH, cierre)
                cierre_final.click()
                sleep(90)
                driver.quit()
            except Exception as e:
                print(f"Ocurrió un error al cerrar la sesion: {e}")
                driver.quit()
        except Exception as e:
            print("⚠️ No se encontraron audios para exportar. Saltando a la siguiente iteración.")
            send_msg(f"⚠️ No se encontraron audios para exportar en la iteración x={x}, i={i}. Saltando a la siguiente iteración.")
            driver.quit()
            return
        
        print("\nIniciando extraccion de archvio zip")
        subprocess.run(["python", "extraccion_archivos.py", f"{str(i)}"])
        sleep(20)
        
        print("\nIniciando movimiento y renombramiento de archivos de audio")
        subprocess.run(["python", "mover_renombrar.py", f"{str(i)}"])
        sleep(2)
        
        print("\nIniciando carga a la base de datos")
        subprocess.run(["python", "carga_base.py", f"{str(i)}"])
        sleep(20)
    except Exception as e:
        intentos_actuales += 1
        intentos_fallidos[iteraccion] = intentos_actuales
        if intentos_actuales < 5:
            print(f"Error en el proceso. Reintentando intento {intentos_actuales}/5 para x={x}, i={i}")
            main(i, x, manual, intentos_fallidos)
        else:
            msg = f"⚠️ Error persistente tras 5 intentos. Falló en interacción x={x}, Campaña i={i}. Deteniendo proceso."
            print(msg)
            send_msg(msg)
            sys.exit(1)
    


if __name__ == '__main__':
    horarios = ["1", "2", "3"]
    intentos_fallidos = {}

    for x in horarios:
        if x == "1":
            send_msg("Iniciando horario 1 de 00:00am a 12:00pm CDMX")
        elif x == "2":
            send_msg("Iniciando horario 2 de 12:00pm a 06:00pm CDMX")
        elif x == "3":
            send_msg("Iniciando horario 3 de 06:00pm a 11:00pm CDMX")
        
        for i in range(3):
            manual = True
            print("\nValor de iteración cdmx-cuernavaca: ", i)
            main(i, x, manual, intentos_fallidos)
