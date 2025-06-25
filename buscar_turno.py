import time
import smtplib, ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests


EMAIL_REMITENTE = "juanicanosa@gmail.com"
EMAIL_DESTINATARIO = "juancanosa450@gmail.com"
EMAIL_PASSWORD = "wkzv uxmt pvrx hbrl"

# Telegram
TOKEN = '7691304523:AAG61IIt4_JxJS5_-jt3wSZdA1hME3-Wg2E'
TELEGRAM_CHAT_IDS = ['5131933506', '6793328512']


def enviar_telegram(mensaje):
    for chat_id in TELEGRAM_CHAT_IDS:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': mensaje
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print(f">> Alerta enviada por Telegram a {chat_id}")
        except Exception as e:
            print(f">> Error al enviar a {chat_id}: {e}")

def enviar_alerta_turno():
    asunto = "🩺 ¡Hay turnos disponibles!"
    mensaje = "El profesional FERNANDEZ, ALEJANDRO tiene horarios disponibles para agendar."

    email_text = f"Subject: {asunto}\n\n{mensaje}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.sendmail(EMAIL_REMITENTE, EMAIL_DESTINATARIO, email_text)

    print(">> ✉️ Mail enviado: hay turnos disponibles.")

def buscar_turno():
    # Declarar las opciones y el servicio DENTRO de la función
    options = Options()
    options.add_argument("--start-maximized")
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(">> Iniciando sesión en COSEM...")
        driver.get("https://portal.cosem.com.uy/PortalWeb/uy.com.ust.hsglogin")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vUSUARIO"))).send_keys("55613999")
        driver.find_element(By.ID, "vPASSWORD").send_keys("Juan.1711")
        btn_entrar = driver.find_element(By.ID, "ENTRAR")
        driver.execute_script("arguments[0].click();", btn_entrar)

        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Agenda")]'))
        ).click()

        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "NUEVOTURNO"))
        ).click()

        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "gxp0_ifrm"))
        )
        driver.switch_to.frame(iframe)

        print(">> Escribiendo FERNANDEZ y presionando Enter")
        search_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "MDSEARCHBAR1Container_navbar"))
        )
        search_input.send_keys("FERNANDEZ")
        search_input.send_keys(u'\ue007')  # Tecla Enter

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[contains(@class,"divTableCell") and contains(., "FERNANDEZ, ALEJANDRO")]/../../..'
            ))
        ).click()
        print(">> Click realizado con éxito")

        # Ver si aparece cartel de "No hay horarios disponibles"
        try:
            ok_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "MaterialDesignMessage_PositiveAction"))
            )
            print(">> Ventana de 'No hay horas disponibles' detectada. Cerrando...")
            ok_btn.click()
            enviar_telegram("🔴 No hay horarios disponibles para FERNANDEZ, ALEJANDRO.")
        except:
            print(">> ✅ No se mostró la ventana de 'No hay horas disponibles' —> Enviando mail...")
            enviar_alerta_turno()
            enviar_telegram("🟢 ¡Hay horarios disponibles para FERNANDEZ, ALEJANDRO!")

    except Exception as e:
        print(f"⚠️ Error durante la ejecución: {e}")
    finally:
        driver.quit()

# --- EJECUCIÓN CADA 10 MINUTOS ---
while True:
    print("\n=======================\n   NUEVO INTENTO\n=======================")
    buscar_turno()
    print(">> Esperando 10 minutos antes del próximo intento...\n")
    time.sleep(600)

