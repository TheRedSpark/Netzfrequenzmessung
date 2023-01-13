import time
import mysql.connector  # 8.0.28
import requests
import math as Math
from package import variables as v
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup  # 20.0a1
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, \
    filters, ConversationHandler  # 20.0a1

on_server = False
version = "1.0"
is_live = True
ort = "server"

if on_server:
    pass
else:
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def user_create(user_id, username):
    mydb = mysql.connector.connect(
        host=v.host(ort),
        user=v.user(ort),
        passwd=v.passwd(ort),
        database=v.database(),
        auth_plugin='mysql_native_password')

    my_cursor = mydb.cursor()
    my_cursor.execute(f"SELECT User_Id,Username FROM `Netzfrequenmessung`.`Users` WHERE User_Id = ({user_id}) ")
    result = my_cursor.fetchone()
    if result is None:
        sql_maske = "INSERT INTO `Netzfrequenmessung`.`Users` (`User_Id`,`Username`) VALUES (%s, %s); "
        data_n = (user_id, username)
        my_cursor.execute(sql_maske, data_n)
        mydb.commit()
    else:
        pass
    my_cursor.close()


def userlogging(user_id, username, message_chat_id, message_txt, message_id, first_name, last_name, land_code):
    mydb = mysql.connector.connect(
        host=v.host(ort),
        user=v.user(ort),
        passwd=v.passwd(ort),
        database=v.database(),
        auth_plugin='mysql_native_password')

    my_cursor = mydb.cursor()
    time_sql = time.strftime("%Y-%m-%d %H:%M:%S")
    if is_live:

        sql_maske = "INSERT INTO `Netzfrequenmessung`.`Messages` (`Time`,`User_Id`,`Username`,`Chat_Id`,`Message_Text`," \
                    "`Message_Id`,`First_Name`,`Last_Name`,`Land_Code`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s); "
        data_n = (
            time_sql, user_id, username, message_chat_id, message_txt, message_id, first_name, last_name, land_code)
        my_cursor.execute(sql_maske, data_n)
        mydb.commit()
        my_cursor.close()

    else:

        sql_maske = "INSERT INTO `Netzfrequenmessung`.`Messagesb` (`Time`,`User_Id`,`Username`,`Chat_Id`,`Message_Text`," \
                    "`Message_Id`,`First_Name`,`Last_Name`,`Land_Code`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s); "
        data_n = (
            time_sql, user_id, username, message_chat_id, message_txt, message_id, first_name, last_name, land_code)
        my_cursor.execute(sql_maske, data_n)
        mydb.commit()
        my_cursor.close()


def netzfrequenz_pull():
    ##Math.round(Math.random()*100000)*31

    x = requests.get('https://netzfrequenzmessung.de:9081/frequenz02a.xml?c=916856')
    y = x.text.splitlines()
    # print(y)
    netzfrequenz = y[1].replace("<f2>", "").replace("</f2>", "")
    zeit = y[3].replace("<z> ", "").replace("</z>", "")

    print(zeit)
    return netzfrequenz


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userlogging(update.effective_user.id, update.effective_user.username, update.effective_message.chat_id,
                update.effective_message.text_markdown, update.effective_message.id, update.effective_user.first_name,
                update.effective_user.last_name, update.effective_user.language_code)
    user_create(update.effective_user.id, update.effective_user.username)
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Der Netzfrequenzmessung-Bot sagt herzlich hallo ;-)\n"
                                        f"Netzfrequenzmessung-Bot V{version}\n")
    await context.bot.send_message(update.effective_user.id,
                                   text=f'Benutze /help um Hilfe mit den Befehlen und der Funktionsweise des Bots zu '
                                        'erhalten. \n')


async def netzfrequenz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userlogging(update.effective_user.id, update.effective_user.username, update.effective_message.chat_id,
                update.effective_message.text_markdown, update.effective_message.id, update.effective_user.first_name,
                update.effective_user.last_name, update.effective_user.language_code)
    frequenz = netzfrequenz_pull()
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Die aktuelle Netzfrequenz beträgt: {frequenz}Hz")


async def mitmachen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userlogging(update.effective_user.id, update.effective_user.username, update.effective_message.chat_id,
                update.effective_message.text_markdown, update.effective_message.id, update.effective_user.first_name,
                update.effective_user.last_name, update.effective_user.language_code)
    await context.bot.send_message(update.effective_user.id,
                                   text=f"https://github.com/TheRedSpark/Netzfrequenzmessung")
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Schau dir gerne das Repo an vielleicht möchtest du dich ja beteiligen.")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userlogging(update.effective_user.id, update.effective_user.username, update.effective_message.chat_id,
                update.effective_message.text_markdown, update.effective_message.id, update.effective_user.first_name,
                update.effective_user.last_name, update.effective_user.language_code)
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Um einen guten Einstieg in das Thema zu erhalten empfehle ich dir diesen C2C3 Talk\n")
    await context.bot.send_message(update.effective_user.id,
                                   text=f"https://www.youtube.com/watch?v=yaCiVvBD-xc\n")


def main() -> None:
    # Creating a telegram bot.
    application = Application.builder().token(v.telegram_netzfrequenz_api(is_live)).build()

    # Adding the handlers for the commands.
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler(["netzfrequenz", "f"], netzfrequenz))
    application.add_handler(CommandHandler(["info", "i"], info))
    application.add_handler(CommandHandler("mitmachen", mitmachen))

    application.run_polling(1)


if __name__ == '__main__':
    main()
