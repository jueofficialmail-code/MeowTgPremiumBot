import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am running on Render.")

if name == 'main':
    # Render မှာ Environment Variable အနေနဲ့ ထည့်မယ့် Token ကို လှမ်းယူပါမယ်
    TOKEN = os.getenv("BOT_TOKEN") 
    
    if not TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        
        # Render Free Tier မှာ Webhook သို့မဟုတ် Polling သုံးနိုင်ပါတယ်
        # ဒီနေရာမှာ အလွယ်ဆုံး Polling စနစ်ကို သုံးထားပါတယ်
        application.run_polling()
