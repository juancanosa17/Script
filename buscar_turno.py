import os
import time
import ssl
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_IDS = os.environ["TELEGRAM_CHAT_IDS"].split(",")
USUARIO_COSEM = os.environ["USUARIO_COSEM"]
PASSWORD_COSEM = os.environ["PASSWORD_COSEM"]

def enviar_telegram(mensaje):
    for chat_id in TELEGRAM_CHAT_IDS:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje}
        try:
            requests.post(url, data=payload)
            print(f"✅ Telegram enviado a {chat_id}")
        except Exception as e:
            print(f"❌ Error al enviar Telegram: {e}")

def buscar_turno():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://portal.cosem.com.uy/PortalWeb/uy.com.ust.hsglogin")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vUSUARIO"))).send_keys(USUARIO_COSEM)
        driver.find_element(By.ID, "vPASSWORD").send_keys(PASSWORD_COSEM)
        btn_entrar = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "ENTRAR"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_entrar)
        driver.execute_script("arguments[0].click();", btn_entrar)

        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Agenda")]'))).click()
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "NUEVOTURNO"))).click()

        iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "gxp0_ifrm")))
        driver.switch_to.frame(iframe)

        search_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "MDSEARCHBAR1Container_navbar")))
        search_input.send_keys("FERNANDEZ")
        search_input.send_keys(Keys.ENTER)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"divTableCell") and contains(., "FERNANDEZ, ALEJANDRO")]/../../..'))
        ).click()
        
        # Esperar máximo 5s a que aparezca alguna señal de resultado
        try:
            WebDriverWait(driver, 5).until_any([
                EC.presence_of_element_located((By.ID, "MaterialDesignMessage_PositiveAction")),
                EC.presence_of_element_located((By.XPATH, "//span[contains(@id,'vHORAGRILLA_')]")),
                EC.presence_of_element_located((By.XPATH, "//img[contains(@src,'Agenda-Nohayhorariosdisponibles.svg')]")),
            ])
        except:
            print("⚠️ Ninguna señal apareció tras hacer clic. Podría haber error de carga o estructura cambiada.")
        
        # Ver si aparece cartel
        try:
            cartel = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.ID, "MaterialDesignMessage_PositiveAction"))
            )
            cartel.click()
            print("🟥 Apareció cartel de 'No hay horarios disponibles'.")
            return
        except:
            pass
        
        # Ver si aparece imagen de "no hay horarios"
        try:
            driver.find_element(By.XPATH, "//img[contains(@src,'Agenda-Nohayhorariosdisponibles.svg')]")
            print("🖼️ Imagen de 'No hay horarios disponibles' detectada.")
            print("🔴 No hay horarios disponibles para FERNANDEZ, ALEJANDRO.")
            return
        except:
            pass
        
        print("✅ Ningún cartel ni imagen detectados. Se buscarán horarios...")

        # --- Esperar explícitamente los horarios ---
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@id,'vHORAGRILLA_')]"))
            )
            elementos_hora = driver.find_elements(By.XPATH, "//span[contains(@id,'vHORAGRILLA_')]")
            horarios = [elem.text.strip() for elem in elementos_hora if elem.text.strip()]
        except Exception as e:
            print(f"⚠️ No se encontraron elementos de horario: {e}")
            horarios = []
        
        cantidad_turnos = len(horarios)
        print(f"🔎 Cantidad de horarios encontrados: {cantidad_turnos}")
        
        if cantidad_turnos > 0:
            mensaje = "🟢 ¡Hay horarios disponibles para FERNANDEZ, ALEJANDRO!\n" + "\n".join(f"- {hora}" for hora in horarios)
            print("🟩 Hay turnos disponibles.")
        else:
            print("🔴 No hay horarios disponibles para FERNANDEZ, ALEJANDRO.")
        
        enviar_telegram(mensaje)

    except Exception as e:
        print(f"⚠️ Error en el proceso: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    buscar_turno()



