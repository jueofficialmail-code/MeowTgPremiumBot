# python-telegram-bot library မှ အရေးကြီးသော module များကို သွင်းယူခြင်း
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ၁။ Bot ၏ Token ကို ဤနေရာတွင် ထည့်သွင်းရန်
# သတိပြုရန်။ ဤနေရာတွင် သင့်ကိုယ်ပိုင် Token ကို အစားထိုးရပါမည်။
TOKEN = "YOUR_BOT_TOKEN_HERE" 

# ၂။ /start command ကို တုံ့ပြန်မည့် function
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command ကို လက်ခံရရှိသည့်အခါ မက်ဆေ့ခ်ျ ပို့သည်"""
    user = update.effective_user
    # MarkdownV2 ကို သုံးထားသောကြောင့် message ကို စာလုံးပြောင်းဖို့ အဆင်ပြေသည်။
    await update.message.reply_html(
        # reply_html ကို သုံးသဖြင့် <b>tag</b> ကို သုံးနိုင်သည်။
        rf"မင်္ဂလာပါ <b>{user.full_name}!</b> ကျွန်တော်သည် စမ်းသပ် Telegram Bot တစ်ခု ဖြစ်ပါသည်။",
        # ဒီနေရာမှာ ကျွန်မလို့ ပြန်ဖြေခိုင်းထားသော်လည်း Bot တစ်ခုဖြစ်သောကြောင့် "ကျွန်တော်" ကိုသာ သုံးနှုန်းပါမည်။
    )

# ၃။ Bot ကို စတင် run မည့် main function
def main() -> None:
    """Bot ကို စတင် run ရန်။"""
    # ApplicationBuilder ကို သုံးပြီး Bot ကို စတင်တည်ဆောက်ခြင်း။
    # TOKEN ကို အသုံးပြုပြီး Bot ကို API နဲ့ ချိတ်ဆက်ခြင်း။
    application = Application.builder().token(TOKEN).build()

    # /start command ကို start_command function နဲ့ ချိတ်ဆက်ပေးခြင်း
    application.add_handler(CommandHandler("start", start_command))

    # Bot ကို စတင်မောင်းနှင်ခြင်း။ Bot ကိုရပ်တန့်ဖို့အတွက် Ctrl+C နှိပ်ပါ။
    print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ၄။ Script ကို စတင် run ပါက main function ကို ခေါ်ခြင်း
if __name__ == "__main__":
    main()
