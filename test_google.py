import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    creds_json = os.environ.get("GOOGLE_CREDS")
    if not creds_json:
        raise Exception("❌ Variável GOOGLE_CREDS não encontrada!")

    try:
        creds_dict = json.loads(creds_json)
    except Exception as e:
        raise Exception("❌ GOOGLE_CREDS não é JSON válido: " + str(e))

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "Teste")
    sheet = client.open(SPREADSHEET_NAME).sheet1

    rows = sheet.get_all_values()[:5]
    print("✅ Conexão bem-sucedida! Primeiras linhas da planilha:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
