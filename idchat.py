import requests

BOT_TOKEN = '7691304523:AAG61IIt4_JxJS5_-jt3wSZdA1hME3-Wg2E'  # Tu token
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)
data = response.json()

print(data)