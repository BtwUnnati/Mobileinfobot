import requests
from random import randint
try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
except ModuleNotFoundError:
    input("There is no necessary library. Complete the command line command: PIP Install Pytelegrambotapi")

url = ""
bot_token = "8240726765:AAFX4a2A9Mp_AJdl1FqUcmGivYsl0q2ksVI"
api_token = "7191462072:sHndGQ1f"
lang = "en"
limit = 300

# Channels to force join - put public username like "@nikumust" OR numeric id like -1001234567890
required_channels = ["@nikumust"]

owner_username = "esxnz"

bot = telebot.TeleBot(bot_token)

# -------- ROBUST MUST JOIN CHECK --------
def check_user_in_channels(user_id):
    """
    Accepts entries in required_channels as:
      - '@username' (public channel username)
      - numeric chat id like -1001234567890 (private channel id)
      - full t.me invite links (https://t.me/+) -> cannot reliably verify; will return False
    Returns True if user is member (or admin/creator/restricted) in ALL channels.
    """
    for channel in required_channels:
        ch = str(channel).strip()
        try:
            # Invite link (t.me/+...) cannot be used with get_chat_member reliably
            if ch.startswith("http://") or ch.startswith("https://"):
                # If it's an invite link (contains +), we cannot verify via API unless bot is in channel and chat has id
                print(f"[check_user_in_channels] Invite-link provided ({ch}) - cannot verify membership via API. Please use @username or numeric chat id.")
                return False

            # If numeric ID given (like -1001234567890)
            if ch.lstrip('-').isdigit():
                chat_identifier = int(ch)
            else:
                # Ensure starts with '@' for username
                chat_identifier = ch if ch.startswith('@') else '@' + ch

            # Try to get the member
            member = bot.get_chat_member(chat_identifier, user_id)
            status = getattr(member, "status", None)
            print(f"[check_user_in_channels] checked {chat_identifier} for user {user_id} -> status: {status}")

            # If left or kicked -> not a member
            if status in ["left", "kicked", None]:
                return False

        except telebot.apihelper.ApiException as e:
            # Common reasons: bot not member of channel, wrong username/id, bot lacks permissions
            print(f"[check_user_in_channels] ApiException for {ch}: {e}")
            return False
        except Exception as e:
            print(f"[check_user_in_channels] Unexpected error for {ch}: {e}")
            return False

    return True
# ---------------------------------------

def user_access_test(user_id):
    return True

cash_reports = {}

def generate_report(query, query_id):
    global cash_reports, url, bot_token, api_token, limit, lang
    # Keep original behavior (even though query.split("") is odd in original code)
    try:
        data = {"token": api_token, "request": query.split("")[0], "limit": limit, "lang": lang}
    except Exception:
        # fallback to whole query
        data = {"token": api_token, "request": query, "limit": limit, "lang": lang}
    try:
        response = requests.post(url, json=data).json()
    except Exception as e:
        print(f"[generate_report] Request failed: {e}")
        return None

    print(response)
    if isinstance(response, dict) and "Error code" in response:
        print("Error:"+response["Error code"])
        return None

    cash_reports[str(query_id)] = []
    # handle missing keys gracefully
    list_dict = response.get("List") if isinstance(response, dict) else None
    if not list_dict:
        return None
    for database_name in list_dict.keys():
        text = [f"<b>{database_name}</b>", ""]
        info = list_dict[database_name].get("InfoLeak", "") if isinstance(list_dict[database_name], dict) else ""
        text.append(info + "")
        if database_name != "No results found":
            for report_data in list_dict[database_name].get("Data", []):
                for column_name in report_data.keys():
                    text.append(f"<b>{column_name}</b>:  {report_data[column_name]}")
                text.append("")
        text = "".join(text)
        if len(text) > 3500:
            text = text[:3500] + " Some data did not fit this message"
        cash_reports[str(query_id)].append(text)
    return cash_reports[str(query_id)]

def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()
    try:
        if page_id < 0:
            page_id = count_page
        elif page_id > count_page - 1:
            page_id = page_id % count_page
    except Exception:
        page_id = 0
    if count_page == 1:
        return markup
    markup.row_width = 3
    markup.add(InlineKeyboardButton(text="<<", callback_data=f"/page {query_id} {page_id-1}"),
               InlineKeyboardButton(text=f"{page_id+1}/{count_page}", callback_data="page_list"),
               InlineKeyboardButton(text=">>", callback_data=f"/page {query_id} {page_id+1}"))
    return markup

# -------- JOIN BUTTON (handles username or full link) --------
def join_alert_keyboard():
    markup = InlineKeyboardMarkup()
    for ch in required_channels:
        chs = str(ch).strip()
        if chs.startswith("http://") or chs.startswith("https://"):
            # use the full link as provided
            markup.add(InlineKeyboardButton(text="Must Join", url=chs))
        else:
            # build t.me link from username (strip @ if provided)
            username = chs.lstrip('@')
            markup.add(InlineKeyboardButton(text="Must Join", url=f"https://t.me/{username}"))
    return markup
# -----------------------------------------------------

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_user_in_channels(user_id):
        bot.send_message(
            message.chat.id,
            "🚫 You must join all required channels to use this bot. Please join and then send /start again.",
            reply_markup=join_alert_keyboard()
        )
        return
    bot.reply_to(message, "Hello! I am a telegram-bot mob to info all supported like car ip address aadhar name etc by toxic nex", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    if not user_access_test(user_id):
        bot.send_message(message.chat.id, "You have no access to the bot")
        return
    if not check_user_in_channels(user_id):
        bot.send_message(
            message.chat.id,
            "🚫 You must join all required channels to use this bot. Please join and try again.",
            reply_markup=join_alert_keyboard()
        )
        return
    if message.content_type == "text":
        query_id = randint(0, 9999999)
        report = generate_report(message.text, query_id)
        if report is None:
            bot.reply_to(message, "The bot does not work at the moment.", parse_mode="Markdown")
            return
        markup = create_inline_keyboard(query_id, 0, len(report))
        try:
            bot.send_message(message.chat.id, report[0], parse_mode="html", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, text=report[0].replace("<b>", "").replace("</b>", ""), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    global cash_reports
    if call.data.startswith("/page "):
        parts = call.data.split(" ")
        if len(parts) < 3:
            return
        query_id, page_id = parts[1], parts[2]
        if query_id not in cash_reports:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="The results of the request have already been deleted")
            except Exception:
                pass
            return
        report = cash_reports[query_id]
        try:
            pid = int(page_id)
        except:
            pid = 0
        markup = create_inline_keyboard(query_id, pid, len(report))
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=report[pid], parse_mode="html", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=report[pid].replace("<b>", "").replace("</b>", ""), reply_markup=markup)
            except Exception:
                pass

while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"[main polling] exception: {e}")
        pass
