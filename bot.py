import os
import telegram
from telegram.ext import Updater, CommandHandler

# os.environ.get() ကို အသုံးပြုပြီး Environment Variable ကနေ Token ကို ဆွဲယူပါ
# BOT_TOKEN_KEY ဆိုတဲ့ နာမည်နဲ့ သင် သတ်မှတ်ရမှာပါ။
BOT_TOKEN = os.environ.get('BOT_TOKEN_KEY') 

# Token မရှိရင် Error ပြရန်
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN_KEY environment variable is not set.")

def start(update, context):
    """/start command ကို ကိုင်တွယ်ဖြေရှင်းခြင်း"""
    update.message.reply_text('Hello from Render! Bot is running securely.')

def main():
    """ဘော့တ်ကို စတင်လည်ပတ်စေခြင်း"""
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    # Render မှာ deploy လုပ်ရင် Webhook ကို အသုံးပြုတာ ပိုကောင်းပေမယ့်၊
    # ရိုးရှင်းစေရန်အတွက် ဒီနမူနာမှာ start_polling() ကို အသုံးပြုထားပါတယ်။
    # ရေရှည်အတွက်ဆိုရင် start_webhook() ကို သုံးသင့်ပါတယ်။
    updater.start_polling() 
    updater.idle()

if __name__ == '__main__':
    main()
    
