import logging
import os
import re
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# =========================================================================
# ⚙️ CONFIGURATION & ENVIRONMENT VARIABLES များကို ရယူခြင်း
# =========================================================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# လုံခြုံရေးအရ Environment Variables ကနေသာ ယူပါမည်။
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Bot Token
ADMIN_CONTACT_USER = os.environ.get("ADMIN_CONTACT_USER", "@admin_contact") 

# Webhook Setup
WEBHOOK_URL = os.environ.get('WEBHOOK_URL') # Render Public URL
PORT = int(os.environ.get('PORT', 8080)) # Render က Port ကိုပေးမထားရင် 8080 ကို သုံးပါ

# =========================================================================
# 🤖 BOT HANDLERS (Command နှင့် Message ကိုင်တွယ်သူများ)
# =========================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command ကို ဖြေကြားပြီး Custom Keyboard ကို ပြပါမည်။"""
    
    # 🌟 Reply Keyboard အတွက် Buttons များ
    keyboard = [
        [KeyboardButton("💰 ဝန်ဆောင်မှုဈေးနှုန်း"), KeyboardButton("❓ အကူအညီလိုတယ်")],
        [KeyboardButton("🔑 ကျွန်ုပ်၏အကောင့်"), KeyboardButton("📞 Admin ကိုဆက်သွယ်မယ်")],
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=False, 
        resize_keyboard=True    
    )
    
    # 📢 အသုံးပြုသူကို စာနဲ့ Keyboard ပြန်ပို့ပါ
    await update.message.reply_text(
        'မင်္ဂလာပါ! Bot မှ ကြိုဆိုပါတယ်။ အောက်ပါ Button များကို နှိပ်ပြီး စတင်နိုင်ပါတယ်။',
        reply_markup=reply_markup
    )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Button နှိပ်တာ (သို့မဟုတ်) စာသား messages တွေကို ကိုင်တွယ်ဖြေရှင်းပေးမယ့် function"""
    
    text = update.message.text
    response = "နားမလည်သေးတဲ့အတွက် တောင်းပန်ပါတယ်။"

    if text == "💰 ဝန်ဆောင်မှုဈေးနှုန်း":
        response = "ဈေးနှုန်းစာရင်းကို ဤနေရာတွင် ကြည့်နိုင်ပါတယ်။"
    elif text == "❓ အကူအညီလိုတယ်":
        response = "အကူအညီအတွက် Admin ကို ဆက်သွယ်နိုင်ပါတယ်။"
    elif text == "🔑 ကျွန်ုပ်၏အကောင့်":
        response = "သင့်အကောင့်အချက်အလက်များကို ပြသပါမည်။"
    elif text == "📞 Admin ကိုဆက်သွယ်မယ်":
        response = f"Admin ကို ဆက်သွယ်ရန်: {ADMIN_CONTACT_USER}"
    
    await update.message.reply_text(response)

# =========================================================================
# 🚀 WEBHOOK SERVER (Flask)
# =========================================================================

def setup_and_run_bot() -> None:
    
    if not BOT_TOKEN or not WEBHOOK_URL:
        logging.error("❌ BOT_TOKEN သို့မဟုတ် WEBHOOK_URL မရှိပါ၊ Bot ကို စတင်နိုင်ခြင်း မရှိပါ။")
        return

    # Bot Application ကို စတင်ဖန်တီးပါ
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handler များကို ထည့်သွင်းပါ
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_click))
    
    # Flask App ကို စတင်ပါ
    app = Flask(__name__)

    @app.post("/")
    async def telegram_webhook():
        """Telegram ကနေ ပို့လာတဲ့ Update တွေကို လက်ခံပြီး Bot ကို လွှဲပြောင်းပေးမယ့် function"""
        data = request.json
        async with application:
            await application.process_update(Update.de_json(data, application.bot))
        return "ok"

    # Flask App ကို Render က ပေးတဲ့ Port မှာ Run ပါ
    logging.info(f"✅ Webhook Server ကို Port {PORT} မှာ စတင်ပါပြီ။")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == '__main__':
    setup_and_run_bot()

