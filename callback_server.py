#callback_server.py
from dotenv import load_dotenv
from flask import Flask, request, render_template_string
from google_auth_oauthlib.flow import Flow
import os
from oauth import save_user_credentials
import bcrypt
from db import check_email_exists, check_password , create_user
from session_store import user_sessions

import asyncio  # Import asyncio at the top of your file


load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = BOT_TOKEN

user_tokens = {}



# Simple login HTML template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f9f9f9; text-align: center; padding-top: 50px; }
        form { background: #fff; padding: 20px; margin: auto; display: inline-block; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { margin: 10px 0; padding: 10px; width: 250px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h2>Login to Continue</h2>
    <form method="POST">
        <input type="hidden" name="user_id" value="{{ user_id }}">
        <input type="email" name="email" placeholder="Enter email" required><br>
        <input type="password" name="password" placeholder="Enter password" required><br>
        <button type="submit">Log In</button>
    </form>
    {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
</body>
</html>
"""
# Temporary session store (in-memory)
user_sessions = {}  # This should be global or imported from a session module

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = request.args.get('user_id') 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email_exists(email) and check_password(email, password):
            # ✅ Save login session
            user_sessions[user_id] = email

            # Use asyncio to call the bot.send_message asynchronously
            asyncio.run(bot.send_message(
                chat_id=user_id,
                text="✅ Login successful! Choose an option below:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📤 Upload File", callback_data='upload')],
                    [InlineKeyboardButton("🔗 Connect Google Drive", callback_data='connect_gdrive')],
                    [InlineKeyboardButton("📂 List Google Drive Files", callback_data='list_gdrive')],
                ])
            ))

            return "<h3>✅ Login successful! You can now return to Telegram.</h3>"
        else:
            return render_template_string(LOGIN_TEMPLATE, user_id=user_id, error="Invalid email or password.")

    return render_template_string(LOGIN_TEMPLATE, user_id=user_id, error=None)

# Sign-Up HTML Template
SIGNUP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sign Up</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f9f9f9; text-align: center; padding-top: 50px; }
        form { background: #fff; padding: 20px; margin: auto; display: inline-block; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { margin: 10px 0; padding: 10px; width: 250px; }
        button { padding: 10px 20px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <h2>Create a New Account</h2>
    <form method="POST">
        <input type="hidden" name="user_id" value="{{ user_id }}">
        <input type="email" name="email" placeholder="Enter email" required><br>
        <input type="password" name="password" placeholder="Enter password" required><br>
        <button type="submit">Sign Up</button>
    </form>
    {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
</body>
</html>
"""

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user_id = request.args.get('user_id') or request.form.get('user_id')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email_exists(email):
            return render_template_string(SIGNUP_TEMPLATE, user_id=user_id, error="Email already registered.")
        else:
            if create_user(email, password):
                # Save session
                user_sessions[user_id] = email
                
                # Send menu options to the user after successful sign-up
                import asyncio
                asyncio.run(bot.send_message(
                    chat_id=user_id,
                    text="✅ Registration successful! Choose an option below:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📤 Upload File", callback_data='upload')],
                        [InlineKeyboardButton("🔗 Connect Google Drive", callback_data='connect_gdrive')],
                        [InlineKeyboardButton("📂 List Google Drive Files", callback_data='list_gdrive')],
                    ])
                ))
                return "<h3>✅ Registration successful! You can now return to Telegram.</h3>"
            else:
                return render_template_string(SIGNUP_TEMPLATE, user_id=user_id, error="Failed to register.")

    return render_template_string(SIGNUP_TEMPLATE, user_id=user_id, error=None)


#google
@app.route("/google/callback")
def google_callback():
    code = request.args.get("code")
    state = request.args.get("state") 

    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/drive.file"],
        redirect_uri='http://localhost:8080/google/callback'
    )

    flow.fetch_token(code=code)

    credentials = flow.credentials
    
    user_tokens[state] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

   
    save_user_credentials(state, credentials)
    return "✅ Google Drive connected successfully! You can close this tab."



if __name__ == "__main__":
    if not os.path.exists("tokens"):
        os.makedirs("tokens")
    app.run(host="0.0.0.0", port=8080)
