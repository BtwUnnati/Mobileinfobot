import requests
from random import randint
try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
except ModuleNotFoundError:
    input("There is no necessary library. Complete the command line command: PIP Install Pytelegrambotapi")

url = "https://leakosintapi.com/"
bot_token = "8240726765:AAFX4a2A9Mp_AJdl1FqUcmGivYsl0q2ksVI"  
api_token = "7191462072:sHndGQ1f" 
lang = "en"
limit = 300


required_channels = [-1001234567890, -1009876543210]  


private_channel_invite_links = [
    "https://t.me/+ft5ilzxnIW1hYzBl",
    "https://t.me/+op6LDmshc785ZGY9"
]


bot = telebot.TeleBot(bot_token)

def user_access_test(user_id):
    return True

def check_user_in_channels(user_id):
    for channel in required_channels:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                return False
        except:
            return False
    return True

cash_reports = {}

def generate_report(query, query_id):
    global cash_reports, url, bot_token, api_token, limit, lang
    data = {"token": api_token, "request": query.split("")[0], "limit": limit, "lang": lang}
    response = requests.post(url, json=data).json()
    print(response)
    if "Error code" in response:
        print("Error:"+response["Error code"])
        return None
    cash_reports[str(query_id)] = []
    for database_name in response["List"].keys():
        text = [f"<b>{database_name}</b>", ""]
        text.append(response["List"][database_name]["InfoLeak"]+"")
        if database_name != "No results found":
            for report_data in response["List"][database_name]["Data"]:
                for column_name in report_data.keys():
                    text.append(f"<b>{column_name}</b>:  {report_data[column_name]}")
                text.append("")
        text = "".join(text)
        if len(text) > 3500:
            text = text[:3500] + text[3500:].split("")[0] + "Some data did not fit this message"
        cash_reports[str(query_id)].append(text)
    return cash_reports[str(query_id)]

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

def join_alert_keyboard():
    markup = InlineKeyboardMarkup()
    buttons = []
    for invite_link in private_channel_invite_links:
        buttons.append(InlineKeyboardButton(text="Must Join Channel", url=invite_link))
    markup.add(*buttons)
    return markup

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
        query_id, page_id = call.data.split(" ")[1:]
        if query_id not in cash_reports:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="The results of the request have already been deleted")
            return
        report = cash_reports[query_id]
        markup = create_inline_keyboard(query_id, int(page_id), len(report))
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=report[int(page_id)], parse_mode="html", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=report[int(page_id)].replace("<b>", "").replace("</b>", ""), reply_markup=markup)

while True:
    try:
        bot.polling()
    except Exception:
        pass
