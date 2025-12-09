import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Environment Variable များမှ Token နှင့် URL ကို ရယူခြင်း
# Render မှာ Environment Variables အဖြစ် သတ်မှတ်ပေးရပါမယ်။
TOKEN = os.environ.get("8150364428:AAEHU8koxGo6Sp_M6JAMFDeRkCgwdh_HBGo")
# Render က ပေးမယ့် URL (ဥပမာ: url)
WEBHOOK_URL = os.environ.get("https://meowtgpremiumbot.onrender.com") 
# Render က ပေးမယ့် Port
PORT = int(os.environ.get("PORT", 5000))

# /start command ကို တုံ့ပြန်မည့် function (မပြောင်းလဲပါ)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command ကို လက်ခံရရှိသည့်အခါ မက်ဆေ့ခ်ျ ပို့သည်"""
    user = update.effective_user
    await update.message.reply_html(
        rf"မင်္ဂလာပါ <b>{user.full_name}!</b> ကျွန်တော် Render မှာ Run နေတဲ့ Bot ဖြစ်ပါတယ်။",
    )

# main function ကို Webhook နဲ့ ကိုက်ညီအောင် ပြင်ဆင်ခြင်း
def main() -> None:
    """Bot ကို စတင် run ရန်။"""
    
    if not TOKEN or not WEBHOOK_URL:
        print("Error: TELEGRAM_BOT_TOKEN or WEBHOOK_URL is not set.")
        # Local စမ်းသပ်မှုများအတွက် Polling ပြန်သုံးနိုင်သည်
        # application = Application.builder().token("YOUR_TOKEN").build()
        # application.run_polling()
        return

    # Webhook စနစ်အတွက် Bot ကို တည်ဆောက်ခြင်း
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))

    # Webhook ကို စတင်သတ်မှတ်ခြင်း
    application.run_webhook(
        listen="0.0.0.0",  # Public Host မှ နားထောင်ခြင်း
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
    print(f"Bot Webhook စတင် အလုပ်လုပ်နေပါပြီ၊ Listening on port {PORT}...")


if __name__ == "__main__":
    main()
    
