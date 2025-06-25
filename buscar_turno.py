import os
import time
import ssl
import smtplib
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL_REMITENTE = os.environ["EMAIL_REMITENTE"]
EMAIL_DESTINATARIO = os.environ["EMAIL_DESTINATARIO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
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

def enviar_alerta_turno():
    asunto = "🩺 ¡Hay turnos disponibles!"
    mensaje = "El profesional FERNANDEZ, ALEJANDRO tiene horarios disponibles."
    email_text = f"Subject: {asunto}\n\n{mensaje}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.sendmail(EMAIL_REMITENTE, EMAIL_DESTINATARIO, email_text)
    print("📧 Mail enviado.")

def buscar_turno():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://portal.cosem.com.uy/PortalWeb/uy.com.ust.hsglogin")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vUSUARIO"))).send_keys(USUARIO_COSEM)
        driver.find_element(By.ID, "vPASSWORD").send_keys(PASSWORD_COSEM)
        driver.find_element(By.ID, "ENTRAR").click()

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

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "MaterialDesignMessage_PositiveAction"))).click()
            print("🟥 No hay turnos.")
            enviar_telegram("🔴 No hay horarios disponibles para FERNANDEZ, ALEJANDRO.")
        except:
            print("🟩 Hay turnos disponibles.")
            enviar_alerta_turno()
            enviar_telegram("🟢 ¡Hay horarios disponibles para FERNANDEZ, ALEJANDRO!")

    except Exception as e:
        print(f"⚠️ Error en el proceso: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    buscar_turno()



