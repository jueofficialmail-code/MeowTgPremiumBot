import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, filters, MessageHandler

# --- Setup & Configuration ---
# Your Bot Token (Replace with your actual token)
BOT_TOKEN = "8150364428:AAHM0W8gHR1Z6ouaSUwEVWJefB-1d1o8XlQ" 

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Quiz Data ---
# Quiz မေးခွန်းများ၊ ရွေးချယ်စရာများ နဲ့ အဖြေမှန်များ
# 
QUIZ_DATA = [
    {
        "question": "ပုဂံပြည်ကို ဘယ်မင်းက စတင်ထူထောင်ခဲ့တာလဲ။",
        "options": ["အနော်ရထာ", "ကျန်စစ်သား", "သမုဒ္ဒရာဇ်", "ပွင့်သကဲ"],
        "correct_answer": "သမုဒ္ဒရာဇ်"
    },
    {
        "question": "မြန်မာနိုင်ငံရဲ့ မြို့တော်က ဘယ်မြို့လဲ။",
        "options": ["ရန်ကုန်", "မန္တလေး", "နေပြည်တော်", "ပုသိမ်"],
        "correct_answer": "နေပြည်တော်"
    },
    {
        "question": "ကမ္ဘာ့အမြင့်ဆုံးတောင် ဘယ်ဟာလဲ။",
        "options": ["ဧဝရက်", "ချင်းမီ", "ပူတာအို", "မေဃာလီ"],
        "correct_answer": "ဧဝရက်"
    }
]

# --- Conversation States ---
QUIZ_START, QUIZ_QUESTION = range(2)

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """စတင်မိတ်ဆက်ပြီး Quiz ကို စဖို့ တောင်းဆိုသည်။"""
    user = update.effective_user
    # ကျွန်မ လို့ ပြန်ဖြေပေးရန်
    await update.message.reply_text(
        f"ဟိုင်း **{user.first_name}**၊ ကျွန်မ Quiz Bot က ကြိုဆိုပါတယ်။ အတာကဏ္ဍကို စတင်ချင်ပါသလား။",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ စတင်မယ်", callback_data='start_quiz')],
            [InlineKeyboardButton("ℹ️ ဘော့အကြောင်း", callback_data='about')]
        ])
    )
    return QUIZ_START

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """အကူအညီ ပေးသည်။"""
    await update.message.reply_text("ဒီဘော့က အတာမေးခွန်းတွေ မေးဖို့ပါ။ /start နှိပ်ပြီး စတင်နိုင်ပါတယ်။")

# --- Callback Query Handlers ---

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inline Keyboard မှ ခလုတ်နှိပ်ခြင်းကို ကိုင်တွယ်သည်။"""
    query = update.callback_query
    await query.answer() # Callback ကို ချက်ချင်း အသိပေးသည်။
    
    data = query.data
    
    if data == 'start_quiz':
        context.user_data['score'] = 0
        context.user_data['current_question_index'] = 0
        return await send_question(query, context)
        
    elif data == 'about':
        await query.edit_message_text("ကျွန်မ က Telegram ပေါ်မှာ အတာမေးခွန်းတွေ မေးဖို့ ရေးထားတဲ့ ဘော့တစ်ခု ဖြစ်ပါတယ်။")
        return ConversationHandler.END # စကားဝိုင်းကို အဆုံးသတ်သည်။
        
    elif data.startswith('answer_'):
        # အဖြေကို စစ်ဆေးသည်။
        answer = data.split('_')[1]
        index = context.user_data.get('current_question_index', 0) - 1
        
        if index < 0 or index >= len(QUIZ_DATA):
            # အခြေအနေမမှန်လျှင်
            await query.edit_message_text("မေးခွန်းရှာမတွေ့ပါ။ /start ကို ပြန်နှိပ်ပါ။")
            return ConversationHandler.END

        current_quiz = QUIZ_DATA[index]
        
        if answer == current_quiz["correct_answer"]:
            context.user_data['score'] += 1
            feedback = "✅ မှန်ကန်ပါတယ်!"
        else:
            feedback = f"❌ မှားသွားပါတယ်။ အဖြေမှန်က **{current_quiz['correct_answer']}** ဖြစ်ပါတယ်။"
            
        # အဖြေစစ်ပြီးနောက် feedback ပေးပြီး နောက်မေးခွန်း ဆက်မေးသည်။
        await query.edit_message_text(f"{current_quiz['question']}\n\nအဖြေ: {answer}\n\n{feedback}")
        
        return await send_question(query, context)
        
    return QUIZ_START

# --- Quiz Logic ---

async def send_question(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """နောက်ထပ် မေးခွန်းတစ်ခု ပေးပို့သည်။"""
    index = context.user_data.get('current_question_index', 0)
    
    if index < len(QUIZ_DATA):
        # မေးခွန်းဆက်မေးရန်
        quiz_item = QUIZ_DATA[index]
        question = quiz_item["question"]
        options = quiz_item["options"]
        
        # Options များကို Inline Keyboard အဖြစ် ပြောင်းလဲသည်။
        keyboard = []
        for option in options:
            # option ကို callback_data မှာ encode လုပ်ပြီးပို့သည်။
            callback_data = f'answer_{option}'
            keyboard.append(InlineKeyboardButton(option, callback_data=callback_data))
            
        # တစ်တန်းမှာ 2 ခု ထားရန်
        keyboard_rows = [keyboard[i:i + 2] for i in range(0, len(keyboard), 2)]
        
        reply_markup = InlineKeyboardMarkup(keyboard_rows)
        
        if hasattr(update_or_query, 'message'):
            # Command ကနေ စတင်လျှင်
            await update_or_query.message.reply_text(
                f"📝 **မေးခွန်း {index + 1}/{len(QUIZ_DATA)}:**\n{question}",
                reply_markup=reply_markup
            )
        else:
            # Callback ကနေ စတင်လျှင် (Message ကို ပြောင်းလဲပါ)
            await update_or_query.edit_message_text(
                f"📝 **မေးခွန်း {index + 1}/{len(QUIZ_DATA)}:**\n{question}",
                reply_markup=reply_markup
            )
            
        context.user_data['current_question_index'] += 1
        return QUIZ_QUESTION
        
    else:
        # မေးခွန်း အားလုံး ပြီးဆုံးလျှင်
        score = context.user_data.get('score', 0)
        total = len(QUIZ_DATA)
        await update_or_query.message.reply_text(
            f"🎉 အတာကဏ္ဍ ပြီးဆုံးပါပြီ။\n\n**ကျွန်မ** ရဲ့ ရမှတ်က **{score}/{total}** ဖြစ်ပါတယ်။\n\n/start ကိုနှိပ်ပြီး အသစ်ပြန်စနိုင်ပါတယ်။"
        )
        # အချက်အလက်များကို ရှင်းပစ်ပါ။
        context.user_data.clear() 
        return ConversationHandler.END

# --- Main Application Setup ---

def main() -> None:
    """ဘော့ကို စတင်သည်။"""
    # ApplicationBuilder ကို အသုံးပြုပြီး Bot ကို တည်ဆောက်သည်။
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Conversation Handler ကို သတ်မှတ်သည်။
    # Entry Points: စကားဝိုင်းစတင်ရန်
    entry_points = [
        CommandHandler("start", start_command)
    ]

    # States: စကားဝိုင်းအတွင်း အခြေအနေများ
    states = {
        QUIZ_START: [
            CallbackQueryHandler(button_callback, pattern='^(start_quiz|about)$')
        ],
        QUIZ_QUESTION: [
            CallbackQueryHandler(button_callback, pattern='^answer_')
        ]
    }
    
    # Fallback: ဘာမှမကိုင်တွယ်နိုင်သောအခါ
    fallbacks = [
        CommandHandler("start", start_command) # start ကို ပြန်နှိပ်နိုင်ရန်
    ]
    
    quiz_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        allow_reentry=True # စကားဝိုင်းထဲမှာ ပြန်ဝင်လို့ရရန်
    )
    
    # Handlers များ ထည့်သွင်းသည်။
    application.add_handler(quiz_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Polling ဖြင့် စတင် run သည်။ (Webhooks အစား)
    logger.info("Bot is starting with Polling...")
    application.run_polling(poll_interval=3)

# --- Flask for Webhooks (Optional but Included) ---

app = Flask(__name__)

# Polling အစား Webhooks သုံးလိုလျှင် အောက်ပါတို့ကို ဖြုတ်ပါ။
# @app.route('/')
# def index():
#     return "Telegram Bot is running!"

# @app.route('/webhook', methods=['POST'])
# async def webhook():
#     update = Update.de_json(request.get_json(force=True), application.bot)
#     await application.update_queue.put(update)
#     return jsonify({'status': 'ok'})

# Flask ကို run လျှင် `if __name__ == '__main__':` ထဲက `main()` ကို ပိတ်ပါ။
# ပြီးလျှင် `application.run_polling()` အစား Webhooks setup ကို ပြင်ဆင်ပါ။

if __name__ == '__main__':
    main()
    # Flask ကို run လိုပါက အောက်ပါအတိုင်း run နိုင်ပါသည်။
    # app.run(host='0.0.0.0', port=5000)

