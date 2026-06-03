import os
import json
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from docxtpl import DocxTemplate

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

OPENAI_API_KEY = "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"
BOT_TOKEN = "8222454597:AAFNm3ZRjtHheAkgXIM9EUAQRDaudvB21Ko"

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_data(text):

    prompt = f"""
Извлеки реквизиты компании из текста.

Верни только JSON.

Поля:
company_name
inn
kpp
ogrn
legal_address
postal_address
director_name
bank_name
bik
checking_account
correspondent_account
okpo
okved
phone
email

Текст:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты извлекаешь реквизиты компаний."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)

def generate_contract(data):

    doc = DocxTemplate("contract_template_final.docx")

    context = {
        "company_name": data.get("company_name", ""),
        "company_name_short": data.get("company_name", ""),
        "inn": data.get("inn", ""),
        "kpp": data.get("kpp", ""),
        "ogrn": data.get("ogrn", ""),
        "legal_address": data.get("legal_address", ""),
        "postal_address": data.get("postal_address", ""),
        "director_name": data.get("director_name", ""),
        "bank_name": data.get("bank_name", ""),
        "bik": data.get("bik", ""),
        "checking_account": data.get("checking_account", ""),
        "correspondent_account": data.get("correspondent_account", ""),
        "okpo": data.get("okpo", ""),
        "okved": data.get("okved", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", "")
    }

    filename = f"contract_{datetime.now().timestamp()}.docx"

    doc.render(context)
    doc.save(filename)

    return filename

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    await update.message.reply_text("Создаю договор...")

    try:

        data = extract_data(text)

        contract_path = generate_contract(data)

        await update.message.reply_document(
            document=open(contract_path, "rb")
        )

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

print("Бот запущен")

app.run_polling()
