import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 🤖 Bot Token ကို Environment Variable ကနေ ရယူခြင်း
# (Render မှာ Setting ထည့်ထားတဲ့ 'BOT_TOKEN' ကို ယူသုံးတာပါ)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Render Web Service ရဲ့ URL ကို Environment Variable ကနေ ရယူခြင်း
# Render က 'RENDER_EXTERNAL_URL' ကို သူ့အလိုလို သတ်မှတ်ပေးပါတယ်
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL") 
PORT = int(os.environ.get("PORT", 8080)) # Render က သုံးမယ့် Port

# 💬 /start command အတွက် Function
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command ကို ဖြေကြားခြင်း။"""
    await update.message.reply_text("မင်္ဂလာပါ ကျွန်မ။ ကျွန်တော်က GitHub, Render, နဲ့ UptimeRobot ကိုသုံးပြီး run ထားတဲ့ Bot ပါ။ ဘယ်လို ကူညီရမလဲ။")

# 🩺 /ping command အတွက် Function (Bot ရှင်သန်နေမနေ စစ်ဆေးရန်)
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot ရှင်သန်နေမနေ စစ်ဆေးခြင်း။"""
    await update.message.reply_text("Pong! ကျွန်တော် အလုပ်လုပ်နေပါတယ်။")

def main() -> None:
    """Bot ကို စတင် run ရန်။"""
    if not BOT_TOKEN or not RENDER_URL:
        print("❌ BOT_TOKEN သို့မဟုတ် RENDER_EXTERNAL_URL ကို မတွေ့ပါ။ Environment Variables ကို စစ်ဆေးပါ။")
        return

    # Application ကို Build လုပ်ခြင်း
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handler များကို ထည့်သွင်းခြင်း
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ping", ping_command))

    # Webhook ကို သတ်မှတ်ခြင်း
    # Webhook path ကို 'telegram-updates' လို့ သတ်မှတ်ထားပါတယ်။
    webhook_url = f"{RENDER_URL}/telegram-updates"
    
    # Render မှာ run ဖို့ Webhook ကို Set လုပ်ပြီး Local Server ကို စောင့်ဆိုင်းစေခြင်း
    print(f"✅ Webhook URL: {webhook_url} ကို သတ်မှတ်နေပါသည်...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram-updates",
        webhook_url=webhook_url,
    )
    print(f"✅ Bot စတင် အလုပ်လုပ်နေပါပြီ (Port: {PORT})")
    
    # UpTimeRobot အတွက် Server ကို စောင့်ဆိုင်းနေစေရန် Dummy HTTP Server ကို run ခြင်း
    # ဒါက UpTimeRobot က Ping လာတဲ့အခါ 200 OK ပြန်ပေးဖို့ဖြစ်ပါတယ်။
    def run_dummy_server():
        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Bot is healthy!")

        httpd = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
        httpd.serve_forever()

    threading.Thread(target=run_dummy_server, daemon=True).start()


if __name__ == "__main__":
    main()

