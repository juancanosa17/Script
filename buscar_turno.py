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
        search_input.send_keys("BERASAIN")
        search_input.send_keys(Keys.ENTER)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"divTableCell") and contains(., "BERASAIN, DANIEL")]/../../..'))
        ).click()

        # --- Detección de días y horarios ---
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@id,'vHORAGRILLA_')]"))
            )
        
            spans_hora = driver.find_elements(By.XPATH, "//span[contains(@id,'vHORAGRILLA_')]")
            spans_dia = driver.find_elements(By.XPATH, "//span[contains(@id,'vTEXTO3_')]")
        
            turnos = []
        
            for span_h in spans_hora:
                id_suffix = span_h.get_attribute("id").split("_")[-1]
                hora = span_h.text.strip()
        
                # Buscar el día correspondiente con el mismo sufijo
                dia = ""
                for span_d in spans_dia:
                    if span_d.get_attribute("id").endswith(id_suffix):
                        dia = span_d.text.strip()
                        break
        
                if hora and dia:
                    turnos.append(f"{dia} - {hora}")
        
        except Exception as e:
            print(f"⚠️ Error al buscar horarios y días: {e}")
            turnos = []
        
        cantidad_turnos = len(turnos)
        print(f"🔎 Cantidad de turnos encontrados: {cantidad_turnos}")
        
        if cantidad_turnos > 0:
            mensaje = "🟢 ¡Hay horarios disponibles para BERASAIN, DANIEL!\n" + "\n".join(f"- {t}" for t in turnos)
            print("🟩 Hay turnos disponibles.")
        else:
            mensaje = "🔴 No hay horarios disponibles para BERASAIN, DANIEL."
            print("🟥 No hay turnos.")
        
        enviar_telegram(mensaje)

    except Exception as e:
        print(f"⚠️ Error en el proceso: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    buscar_turno()



