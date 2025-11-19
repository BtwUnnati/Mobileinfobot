import requests
from random import randint
import json
import os
try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
except ModuleNotFoundError:
    input("There is no necessary library. Complete the command line command: pip install pytelegrambotapi")

url = "https://leakosintapi.com/"
bot_token = "8395895550:AAE8ucM2C_YZ76vAxcA7zInt1Nv41Fcm6NQ"
api_token = "5724339297:eYRu5pu4"
lang = "en"
limit = 300

# Admin configuration
ADMIN_ID = 8294942940  # Yaha apna admin Telegram user ID dale
FORCE_JOIN_CHANNEL = "ToxicTechz"  # Yaha apna channel username dale (@ ke sath)
ADMIN_USERNAME = "@esxnz"  # Buy ke liye admin username

# Credit database file
CREDITS_FILE = "user_credits.json"

# Load credits from file
def load_credits():
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save credits to file
def save_credits():
    with open(CREDITS_FILE, 'w') as f:
        json.dump(user_credits, f, indent=4)

user_credits = load_credits()

# Check if user is member of channel
def is_user_member(user_id):
    try:
        member = bot.get_chat_member(FORCE_JOIN_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Get user credits
def get_credits(user_id):
    user_id_str = str(user_id)
    if user_id_str not in user_credits:
        user_credits[user_id_str] = 20  # Free 20 credits for new users
        save_credits()
    return user_credits[user_id_str]

# Deduct credits
def deduct_credits(user_id, amount=2):
    user_id_str = str(user_id)
    if user_id_str in user_credits:
        user_credits[user_id_str] -= amount
        save_credits()
        return True
    return False

# Add credits (admin only)
def add_credits(user_id, amount):
    user_id_str = str(user_id)
    if user_id_str not in user_credits:
        user_credits[user_id_str] = 0
    user_credits[user_id_str] += amount
    save_credits()

# Function for generating reports
cash_reports = {}
def generate_report(query, query_id):
    global cash_reports, url, bot_token, api_token, limit, lang
    data = {"token": api_token, "request": query.split("")[0], "limit": limit, "lang": lang}
    response = requests.post(url, json=data).json()
    print(response)
    if "Error code" in response:
        print("Error:" + response["Error code"])
        return None
    cash_reports[str(query_id)] = []
    for database_name in response["List"].keys():
        text = [f"<b>{database_name}</b>", ""]
        text.append(response["List"][database_name]["InfoLeak"] + "
")
        if database_name != "No results found":
            for report_data in response["List"][database_name]["Data"]:
                for column_name in report_data.keys():
                    text.append(f"<b>{column_name}</b>:  {report_data[column_name]}")
                text.append("")
        text = "
".join(text)
        if len(text) > 3500:
            text = text[:3500] + text[3500:].split("
")[0] + "

Some data did not fit this message"
        cash_reports[str(query_id)].append(text)
    return cash_reports[str(query_id)]

# Function for creating inline keyboard
def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()
    if page_id < 0:
        page_id = count_page
    elif page_id > count_page - 1:
        page_id = page_id % count_page
    if count_page == 1:
        return markup
    markup.row_width = 3
    markup.add(InlineKeyboardButton(text="<<", callback_data=f"/page {query_id} {page_id-1}"),
               InlineKeyboardButton(text=f"{page_id+1}/{count_page}", callback_data="page_list"),
               InlineKeyboardButton(text=">>", callback_data=f"/page {query_id} {page_id+1}"))
    return markup

# Force join keyboard
def force_join_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{FORCE_JOIN_CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="✅ Verify", callback_data="verify_join"))
    return markup

# Main menu keyboard
def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(text="💳 My Credits", callback_data="check_credits"),
        InlineKeyboardButton(text="🛒 Buy Credits", callback_data="buy_credits")
    )
    markup.add(
        InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
        InlineKeyboardButton(text="📊 Stats", callback_data="stats")
    )
    return markup

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    
    # Check if user is member
    if not is_user_member(user_id):
        bot.send_message(
            message.chat.id,
            "❌ <b>Access Denied!</b>

"
            "Please join our channel to use this bot.
"
            "After joining, click 'Verify' button below.",
            parse_mode="html",
            reply_markup=force_join_keyboard()
        )
        return
    
    # Initialize credits for new users
    credits = get_credits(user_id)
    
    welcome_text = (
        f"👋 <b>Welcome to Info Search Bot!</b>

"
        f"💰 Your Credits: <b>{credits}</b>

"
        f"📌 You can search for:
"
        f"• Car details
"
        f"• IP Address info
"
        f"• Aadhar details
"
        f"• Name search
"
        f"• And more...

"
        f"💸 Each search costs <b>2 credits</b>

"
        f"Choose an option below:"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="html",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(commands=["add"])
def add_credits_command(message):
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    
    try:
        # Parse command: /add @username 50
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Usage: /add @username credits
Example: /add @john 50")
            return
        
        target_username = parts[1]
        credits_to_add = int(parts[2])
        
        # Get user ID from username (you'll need to track this or use user_id directly)
        bot.reply_to(
            message,
            f"⚠️ Please use user ID instead of username.
"
            f"Usage: /add USER_ID credits
"
            f"Example: /add 123456789 50"
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid credits amount. Please enter a number.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=["addcredits"])
def add_credits_by_id(message):
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Usage: /addcredits USER_ID credits
Example: /addcredits 123456789 50")
            return
        
        target_user_id = int(parts[1])
        credits_to_add = int(parts[2])
        
        add_credits(target_user_id, credits_to_add)
        
        bot.reply_to(
            message,
            f"✅ Successfully added <b>{credits_to_add}</b> credits to user <code>{target_user_id}</code>
"
            f"New balance: <b>{get_credits(target_user_id)}</b> credits",
            parse_mode="html"
        )
        
        # Notify user
        try:
            bot.send_message(
                target_user_id,
                f"🎉 <b>Credits Added!</b>

"
                f"Admin has added <b>{credits_to_add}</b> credits to your account.
"
                f"Your new balance: <b>{get_credits(target_user_id)}</b> credits",
                parse_mode="html"
            )
        except:
            pass
            
    except ValueError:
        bot.reply_to(message, "❌ Invalid format. Use numbers only.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    
    # Check if user is member
    if not is_user_member(user_id):
        bot.send_message(
            message.chat.id,
            "❌ <b>Channel Join Required!</b>

"
            "Please join our channel first to use this bot.",
            parse_mode="html",
            reply_markup=force_join_keyboard()
        )
        return
    
    if message.content_type == "text":
        # Check credits
        credits = get_credits(user_id)
        if credits < 2:
            bot.send_message(
                message.chat.id,
                f"❌ <b>Insufficient Credits!</b>

"
                f"Your balance: <b>{credits}</b> credits
"
                f"Required: <b>2</b> credits per search

"
                f"💰 Buy more credits by contacting: {ADMIN_USERNAME}",
                parse_mode="html"
            )
            return
        
        # Deduct credits
        deduct_credits(user_id, 2)
        new_balance = get_credits(user_id)
        
        query_id = randint(0, 9999999)
        report = generate_report(message.text, query_id)
        markup = create_inline_keyboard(query_id, 0, len(report) if report else 0)
        
        if report == None:
            bot.reply_to(message, "❌ The bot does not work at the moment.", parse_mode="Markdown")
            # Refund credits on error
            add_credits(user_id, 2)
        else:
            try:
                result_text = f"{report[0]}

💳 Credits used: 2
💰 Remaining: {new_balance}"
                bot.send_message(message.chat.id, result_text, parse_mode="html", reply_markup=markup)
            except telebot.apihelper.ApiTelegramException:
                result_text = f"{report[0].replace('<b>','').replace('</b>','')}

💳 Credits used: 2
💰 Remaining: {new_balance}"
                bot.send_message(message.chat.id, text=result_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    global cash_reports
    user_id = call.from_user.id
    
    if call.data == "verify_join":
        if is_user_member(user_id):
            credits = get_credits(user_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ <b>Verification Successful!</b>

"
                     f"🎉 Welcome! You have received <b>20 free credits</b>

"
                     f"Type any query to start searching!",
                parse_mode="html",
                reply_markup=main_menu_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)
    
    elif call.data == "check_credits":
        credits = get_credits(user_id)
        bot.answer_callback_query(call.id, f"💰 Your Credits: {credits}", show_alert=True)
    
    elif call.data == "buy_credits":
        bot.send_message(
            call.message.chat.id,
            f"💳 <b>Buy Credits</b>

"
            f"Contact admin to purchase credits:
"
            f"👤 Admin: {ADMIN_USERNAME}

"
            f"💰 Current balance: <b>{get_credits(user_id)}</b> credits",
            parse_mode="html"
        )
    
    elif call.data == "help":
        help_text = (
            "📖 <b>How to Use</b>

"
            "1️⃣ Send any search query (name, phone, email, etc.)
"
            "2️⃣ Bot will search and show results
"
            "3️⃣ Each search costs 2 credits

"
            "💡 <b>Tips:</b>
"
            "• Make sure your query is accurate
"
            "• Use specific details for better results
"
            "• Check your credits before searching"
        )
        bot.send_message(call.message.chat.id, help_text, parse_mode="html")
    
    elif call.data == "stats":
        credits = get_credits(user_id)
        searches_made = (20 - credits) // 2 if credits <= 20 else 0
        bot.send_message(
            call.message.chat.id,
            f"📊 <b>Your Statistics</b>

"
            f"💰 Credits: <b>{credits}</b>
"
            f"🔍 Searches made: <b>{searches_made}</b>
"
            f"🆔 User ID: <code>{user_id}</code>",
            parse_mode="html"
        )
    
    elif call.data.startswith("/page "):
        query_id, page_id = call.data.split(" ")[1:]
        if not (query_id in cash_reports):
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="The results of the request have already been deleted"
            )
        else:
            report = cash_reports[query_id]
            markup = create_inline_keyboard(query_id, int(page_id), len(report))
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=report[int(page_id)],
                    parse_mode="html",
                    reply_markup=markup
                )
            except telebot.apihelper.ApiTelegramException:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=report[int(page_id)].replace("<b>", "").replace("</b>", ""),
                    reply_markup=markup
                )

while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: {e}")
        pass
