import logging
import os # os module ကို import လုပ်ရန် ထည့်သွင်းပေးလိုက်သည်
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler

# --- Setup & Configuration ---
# Your Bot Token (Replace with your actual token)
# သင့် Bot Token သည် ဤနေရာတွင် အဆင်သင့် ဖြစ်နေပြီ။
BOT_TOKEN = "8150364428:AAHM0W8gHR1Z6ouaSUwEVWJefB-1d1o8XlQ" 
RENDER_URL = "YOUR_RENDER_SERVICE_URL" # *** ဤနေရာတွင် သင့် Render Service URL ကို ထည့်ရန် လိုအပ်သည် ***

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Quiz Data ---
# Quiz မေးခွန်းများ၊ ရွေးချယ်စရာများ နဲ့ အဖြေမှန်များ
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
    await query.answer() 
    
    data = query.data
    
    if data == 'start_quiz':
        context.user_data['score'] = 0
        context.user_data['current_question_index'] = 0
        return await send_question(query, context)
        
    elif data == 'about':
        await query.edit_message_text("ကျွန်မ က Telegram ပေါ်မှာ အတာမေးခွန်းတွေ မေးဖို့ ရေးထားတဲ့ ဘော့တစ်ခု ဖြစ်ပါတယ်။")
        return ConversationHandler.END 
        
    elif data.startswith('answer_'):
        answer = data.split('_')[1]
        index = context.user_data.get('current_question_index', 0) - 1
        
        if index < 0 or index >= len(QUIZ_DATA):
            await query.edit_message_text("မေးခွန်းရှာမတွေ့ပါ။ /start ကို ပြန်နှိပ်ပါ။")
            return ConversationHandler.END

        current_quiz = QUIZ_DATA[index]
        
        if answer == current_quiz["correct_answer"]:
            context.user_data['score'] += 1
            feedback = "✅ မှန်ကန်ပါတယ်!"
        else:
            feedback = f"❌ မှားသွားပါတယ်။ အဖြေမှန်က **{current_quiz['correct_answer']}** ဖြစ်ပါတယ်။"
            
        await query.edit_message_text(f"{current_quiz['question']}\n\nအဖြေ: {answer}\n\n{feedback}")
        
        return await send_question(query, context)
        
    return QUIZ_START

# --- Quiz Logic ---

async def send_question(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """နောက်ထပ် မေးခွန်းတစ်ခု ပေးပို့သည်။"""
    index = context.user_data.get('current_question_index', 0)
    
    if index < len(QUIZ_DATA):
        quiz_item = QUIZ_DATA[index]
        question = quiz_item["question"]
        options = quiz_item["options"]
        
        keyboard = []
        for option in options:
            callback_data = f'answer_{option}'
            keyboard.append(InlineKeyboardButton(option, callback_data=callback_data))
            
        keyboard_rows = [keyboard[i:i + 2] for i in range(0, len(keyboard), 2)]
        
        reply_markup = InlineKeyboardMarkup(keyboard_rows)
        
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(
                f"📝 **မေးခွန်း {index + 1}/{len(QUIZ_DATA)}:**\n{question}",
                reply_markup=reply_markup
            )
        else:
            await update_or_query.edit_message_text(
                f"📝 **မေးခွန်း {index + 1}/{len(QUIZ_DATA)}:**\n{question}",
                reply_markup=reply_markup
            )
            
        context.user_data['current_question_index'] += 1
        return QUIZ_QUESTION
        
    else:
        score = context.user_data.get('score', 0)
        total = len(QUIZ_DATA)
        # update_or_query မှာ query object ဖြစ်နေရင် message.reply_text ကို ခေါ်လို့မရဘူး။
        # ဒါကြောင့် query ဖြစ်မဖြစ် စစ်ပြီး edit_message_text ကို သုံးရမည်။
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(
                f"🎉 အတာကဏ္ဍ ပြီးဆုံးပါပြီ။\n\n**ကျွန်မ** ရဲ့ ရမှတ်က **{score}/{total}** ဖြစ်ပါတယ်။\n\n/start ကိုနှိပ်ပြီး အသစ်ပြန်စနိုင်ပါတယ်။"
            )
        else:
            await update_or_query.edit_message_text(
                f"🎉 အတာကဏ္ဍ ပြီးဆုံးပါပြီ။\n\n**ကျွန်မ** ရဲ့ ရမှတ်က **{score}/{total}** ဖြစ်ပါတယ်။\n\n/start ကိုနှိပ်ပြီး အသစ်ပြန်စနိုင်ပါတယ်။"
            )

        context.user_data.clear() 
        return ConversationHandler.END

# --- Application Setup ---

application = ApplicationBuilder().token(BOT_TOKEN).build()
app = Flask(__name__)
# Render မှ ပေးသော Port ကို ယူပါ (Default 10000)
PORT = int(os.environ.get('PORT', '10000')) 


def setup_handlers(app_instance) -> None:
    """Handlers များကို ApplicationBuilder instance တွင် ထည့်သွင်းသည်"""
    entry_points = [
        CommandHandler("start", start_command)
    ]

    states = {
        QUIZ_START: [
            CallbackQueryHandler(button_callback, pattern='^(start_quiz|about)$')
        ],
        QUIZ_QUESTION: [
            CallbackQueryHandler(button_callback, pattern='^answer_')
        ]
    }
    
    fallbacks = [
        CommandHandler("start", start_command)
    ]
    
    quiz_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        allow_reentry=True
    )
    
    app_instance.add_handler(quiz_handler)
    app_instance.add_handler(CommandHandler("help", help_command))

# --- Flask Webhook Handlers ---

@app.route('/')
def index():
    """Render Health Check အတွက်"""
    return "MaooTgPremiumBot is running and ready for webhooks!"

@app.route('/webhook', methods=['POST'])
async def webhook_handler():
    """Telegram ကနေ ပို့လာတဲ့ Webhook Updates တွေကို ကိုင်တွယ်ဖို့"""
    if request.method == "POST":
        # application.process_update() ကို အသုံးပြုပြီး Update ကို ကိုင်တွယ်သည်။
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok"

# --- Main Run Block ---

if __name__ == '__main__':
    setup_handlers(application)
    
    # Webhook URL ကို တစ်ခါတည်း သတ်မှတ်သည်။
    # RENDER_URL ကို သင့်ကိုယ်ပိုင် URL ဖြင့် အစားထိုးရန် လိုအပ်ပါသည်။
    if RENDER_URL != "https://meowtgpremiumbot.onrender.com":
        webhook_url = f"{RENDER_URL}/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        # Blocking function ကို run နိုင်ရန် asyncio ကို သုံးနိုင်သည်။ 
        # သို့သော် gunicorn သည် Bot ကို run မည်ဆိုလျှင်၊ ဒီနေရာကို ဖြုတ်ပြီး 
        # browser ဖြင့် setWebhook ကို ကိုယ်တိုင် ပြုလုပ်ခြင်းက ပိုလုံခြုံပါသည်။
        # try/except ဖြင့် setWebhook ကို run နိုင်ပါသည်။
    
    # Gunicorn ဖြင့် run လျှင် Flask application `app` ကိုသာ run မည်။
    # Flask app ကို debug mode ဖြင့် local မှာ run လိုလျှင် အောက်ပါအတိုင်း run နိုင်ပါသည်။
    # app.run(host='0.0.0.0', port=PORT, debug=True)
    logger.info("Bot is ready. Please run with gunicorn on Render.")

