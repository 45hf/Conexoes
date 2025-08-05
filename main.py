import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import os

# === CONFIGURAÇÕES ===
SPREADSHEET_NAME = 'Teste'
SHRINKEARN_API_TOKEN = '2ff51993a5ffc8bcde27e96b79a5b56d7fc7ea51'
TELEGRAM_BOT_TOKEN = '7809845840:AAH5EfK-pijoAY8raiS51-mLezktLTNOC6w'
TELEGRAM_CHANNEL_ID = '-1002860521899'
REPLIT_BASE_URL = 'https://camuflagem-links.mgermano724.repl.co'

# === AUTENTICAÇÃO COM GOOGLE SHEETS ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope)
client = gspread.authorize(credentials)

# === ACESSA A PLANILHA ===
sheet = client.open(SPREADSHEET_NAME).sheet1

# === INICIA O BOT ===
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# === PEGA TODAS AS LINHAS ===
rows = sheet.get_all_records()
print(f"🔍 Total de linhas lidas: {len(rows)}")

contador_arquivo = 1

for i, row in enumerate(rows, start=2):
    print(f"\n➡️ Processando Linha {i}: {row}")

    link_original = row.get("Link Original")
    link_encurtado = row.get("Link Encurtado")

    if link_original and not link_encurtado:
        try:
            print(f"✂️ Encurtando: {link_original}")
            response = requests.get(
                "https://shrinkearn.com/api",
                params={"api": SHRINKEARN_API_TOKEN, "url": link_original},
                timeout=10
            )
            data = response.json()

            if data.get("status") == "success":
                short_link = data["shortenedUrl"]
                nome_arquivo = f"link{contador_arquivo}.html"
                contador_arquivo += 1

                # === CRIA ARQUIVO HTML COM REDIRECIONAMENTO ===
                html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0; URL='{short_link}'" />
  <title>Redirecionando...</title>
</head>
<body>
  <p>Redirecionando, aguarde...</p>
</body>
</html>"""
                with open(nome_arquivo, "w", encoding="utf-8") as f:
                    f.write(html_content)

                camuflado_url = f"{REPLIT_BASE_URL}/{nome_arquivo}"

                # === ATUALIZA A PLANILHA ===
                sheet.update_cell(i, 4, camuflado_url)  # Coluna D
                sheet.update_cell(i, 5, datetime.now().strftime("%d/%m/%Y"))  # Coluna E
                sheet.update_cell(i, 6, "Enviado")  # Coluna F

                # === ENVIA PARA TELEGRAM ===
                mensagem = f"🔗 {row.get('Nome do Link')}\n{camuflado_url}"
                bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=mensagem)
                print(f"✅ Link camuflado enviado: {camuflado_url}")
            else:
                print(f"⚠️ Erro no ShrinkEarn: {data}")
        except Exception as e:
            print(f"❌ Erro: {e}")

print("\n🚀 Bot finalizou o processamento da planilha com sucesso!")
