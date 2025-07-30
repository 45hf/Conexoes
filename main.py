import gspread
import requests
from datetime import datetime
from telegram import Bot
from oauth2client.service_account import ServiceAccountCredentials

# CONFIGURAÇÕES
SPREADSHEET_NAME = 'Teste'
SHRINKEARN_API_TOKEN = '2ff51993a5ffc8bcde27e96b79a5b56d7fc7ea51'
TELEGRAM_BOT_TOKEN = '7809845840:AAH5EfK-pijoAY8raiS51-mLezktLTNOC6w'
TELEGRAM_CHANNEL_ID = '-1002860521899'

# AUTENTICAÇÃO COM GOOGLE SHEETS
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)

# ACESSAR PLANILHA
sheet = client.open(SPREADSHEET_NAME).sheet1

# INICIAR BOT TELEGRAM
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# LER TODAS AS LINHAS DA PLANILHA
rows = sheet.get_all_records()
print(f"🔍 Total de linhas lidas: {len(rows)}")

# PERCORRER AS LINHAS A PARTIR DA LINHA 2
for i, row in enumerate(rows, start=2):
    print(f"➡️ Linha {i}: {row}")

    link_original = row.get("Link Original")
    link_encurtado = row.get("Link Encurtado")
    nome_do_link = row.get("Nome do Link")

    if link_original and not link_encurtado:
        print(f"🔗 Encurtando: {link_original}")

        # CHAMAR API DO SHRINKEARN
        response = requests.get(
            f"https://shrinkearn.com/api?api={SHRINKEARN_API_TOKEN}&url={link_original}"
        )
        data = response.json()

        if data["status"] == "success":
            short_link = data["shortenedUrl"]

            # ATUALIZAR PLANILHA
            sheet.update_cell(i, 4, short_link)  # Coluna D - Link Encurtado
            sheet.update_cell(i, 5, datetime.now().strftime("%d/%m/%Y"))  # Coluna E - Data

            # ENVIAR PARA TELEGRAM
            mensagem = f"🔗 {nome_do_link or 'Link'}\n{short_link}"
            bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=mensagem)

            print(f"✅ Enviado para o Telegram: {short_link}")
        else:
            print(f"⚠️ Erro ao encurtar link: {link_original}")
