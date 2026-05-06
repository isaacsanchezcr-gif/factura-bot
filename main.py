import os
import base64
import httpx
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_KEY = os.environ["OPENAI_KEY"]

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Recibí tu factura, analizando...")
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    image_b64 = base64.b64encode(photo_bytes).decode()
    
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    {"type": "text", "text": "Sos un contador de Costa Rica. Extraé los datos de esta factura y respondé así:\n\n🧾 FACTURA\nNúmero: ...\nFecha: ...\n\n👤 EMISOR\nNombre: ...\nCédula: ...\n\n👤 RECEPTOR\nNombre: ...\nCédula: ...\n\n📋 DETALLE\n- [descripción] x[cantidad] = ₡[subtotal]\n\n💰 TOTALES\nSubtotal: ₡...\nIVA (13%): ₡...\nTOTAL: ₡...\n\nSi no ves algún dato escribí No visible."}
                ]
            }]
        },
        timeout=30
    )
    
    result = response.json()
    text = result["choices"][0]["message"]["content"]
    await update.message.reply_text(text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola! Mandame una foto de tu factura y la proceso.")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT, handle_text))

if __name__ == "__main__":
    app.run_polling()
  
