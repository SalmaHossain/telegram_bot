from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import  ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
from oauth import generate_google_oauth_url, upload_to_google_drive, list_drive_files, search_drive_files
import threading
from callback_server import app as flask_app
from urllib.parse import quote
from session_store import user_sessions
from telegram.ext import CallbackContext
from oauth import search_drive_for_text


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Temporary session data
user_states = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Log In", callback_data='login')],
        [InlineKeyboardButton("⚒ Sign Up", callback_data='signup')]
    ]
    await update.message.reply_text("Welcome! Please log in to continue.", reply_markup=InlineKeyboardMarkup(keyboard))

# Button clicks (login/signup/menu)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'login':
        login_url = f"https://13df-103-231-161-213.ngrok-free.app/login?user_id={user_id}"
        await query.message.reply_text(
            "🔐 To log in, please open your web browser and visit the following URL:\n"
            f"`{login_url}`\n\n"
            "Manually type or paste it into your browser's address bar.",
            parse_mode="Markdown"
        )
    
    elif query.data == 'signup':
        signup_url = f"https://13df-103-231-161-213.ngrok-free.app/signup?user_id={user_id}"
        await query.message.reply_text(
            "🛠️ To sign up, please open your web browser and visit the following URL:\n"
            f"`{signup_url}`\n\n"
            "Manually type or paste it into your browser's address bar.",
            parse_mode="Markdown"
        )


    elif query.data == 'upload':
        await query.message.reply_text("📁 Please send the file you want to upload.")
   
    elif query.data == 'connect_gdrive':
        gdrive_url = generate_google_oauth_url(str(user_id))
        await query.message.reply_text(f"🔐 Click to connect your Google Drive:\n{gdrive_url}")

    elif query.data == 'list_gdrive':
        try:
            files = list_drive_files(str(user_id))
            if files:
                reply = "\n".join(f"📄 {file['name']} - https://drive.google.com/file/d/{file['id']}/view" for file in files)
            else:
                reply = "📂 No files found in your Google Drive."
        except Exception as e:
            reply = "❌ Error accessing your Google Drive. Please connect again."
        await query.message.reply_text(reply)
    
    elif query.data == 'search_gdrive':
        await query.message.reply_text("🔍 Please type the query you'd like to search for in your Google Drive files.")


       


# Handles all user input
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id, {})
    query = update.message.text.strip()

    if text == "🔗 Connect Google Drive":
        auth_url = generate_google_oauth_url(str(user_id))
        await update.message.reply_text(
            f"🌐 [Click here to connect Google Drive]({auth_url})", parse_mode='Markdown'
        )
    
    if text.startswith("🔗 Connect Google Drive"):
        auth_url = generate_google_oauth_url(str(user_id))
        await update.message.reply_text(
            f"🌐 [Click here to connect Google Drive]({auth_url})", parse_mode='Markdown'
        )
    else:  # Process search query
        try:
            result = search_drive_files(str(user_id), text)
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Error searching files: {e}")
       

    # Handle search query
    try:
        response = search_drive_files(str(user_id), query)
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"❌ Error searching files: {e}")


# File upload handler
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    document = update.message.document

    if not document:
        await update.message.reply_text("❌ No file found in message.")
        return

    file = await document.get_file()
    file_path = f"{user_id}_{document.file_name}"
    await file.download_to_drive(file_path)
    await update.message.reply_text("📤 Uploading your file to Google Drive...")

    try:
        success = upload_to_google_drive(user_id, file_path)
        if success:
            await update.message.reply_text("✅ File uploaded to your Google Drive!")
        else:
            await update.message.reply_text("⚠️ Failed to upload file. Please authenticate first.")
    except Exception as e:
        await update.message.reply_text(f"❌ Upload error: {e}")

async def login_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    login_url = f"https://13df-103-231-161-213.ngrok-free.app/login?user_id={quote(str(user_id))}"
    
    await query.message.reply_text(
        f'🔐 <a href="{login_url}">Click here to log in securely</a>',
        parse_mode="HTML",
        disable_web_page_preview=True
    )







# Start Flask server
def run_flask():
    flask_app.run(port=8080)

# Main entry
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("✅ Bot and Flask server running...")
    app.run_polling()

if __name__ == "__main__":
    main()
