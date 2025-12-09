import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. Define Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="မင်္ဂလာပါ! Render ပေါ်မှာ Bot အောင်မြင်စွာ Run နေပါပြီ။"
    )

# 3. Main execution block
if __name__ == '__main__':
    # Get the token from environment variables
    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        # Inform the user if the token is missing
        print("Error: BOT_TOKEN is missing! Please check Environment Variables in Render.")
    else:
        # Build and configure the Telegram Bot application
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Add the /start command handler
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        
        print("Bot is starting...")
        # Start the bot using polling to listen for new updates
        application.run_polling()

