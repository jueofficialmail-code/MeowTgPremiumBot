import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Logging စနစ် (Error တက်ရင် မြင်ရအောင် ထည့်ထားခြင်းဖြစ်သည်)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. /start နှိပ်ရင် အလုပ်လုပ်မည့် Function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="မင်္ဂလာပါ! Render ပေါ်မှာ Bot အောင်မြင်စွာ Run နေပါပြီ။"
    )

# 3. Main Program
if name == 'main':
    # Render Environment Variable ထဲက Token ကို လှမ်းယူမယ်
    TOKEN = os.getenv("BOT_TOKEN")

    # Token မရှိရင် Run လို့မရအောင် စစ်ဆေးမယ် (Error ကာကွယ်ရန်)
    if not TOKEN:
        print("Error: BOT_TOKEN is missing! Please check Environment Variables in Render.")
    else:
        # Bot ကို တည်ဆောက်မယ်
        application = ApplicationBuilder().token(TOKEN).build()
        
        # /start command ကို လက်ခံဖို့ သတ်မှတ်မယ်
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        
        # Bot ကို စတင် Run မယ်
        print("Bot is starting...")
        application.run_polling()
