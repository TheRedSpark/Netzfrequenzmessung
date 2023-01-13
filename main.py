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

if on_server:
    pass
else:
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def netzfrequenz_pull():
    ##Math.round(Math.random()*100000)*31

    x = requests.get('https://netzfrequenzmessung.de:9081/frequenz02a.xml?c=916856')
    y = x.text.splitlines()
    # print(y)
    netzfrequenz = y[1].replace("<f2>", "").replace("</f2>", "")
    zeit = y[3].replace("<z> ", "").replace("</z>", "")

    print(zeit)
    print(netzfrequenz)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Der Netzfrequenzmessung-Bot sagt herzlich hallo ;-)\n"
                                        f"Netzfrequenzmessung-Bot {version}")
    await context.bot.send_message(update.effective_user.id,
                                   text=f'Benutze /help um Hilfe mit den Befehlen und der Funktionsweise des Bots zu '
                                        'erhalten. \n')


def main() -> None:
    # Creating a telegram bot.
    application = Application.builder().token(v.telegram_netzfrequenz_api(is_live)).build()

    # Adding the handlers for the commands.
    application.add_handler(CommandHandler(["start", "help"], start))

    application.run_polling(1)


if __name__ == '__main__':
    main()
