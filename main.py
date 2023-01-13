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
                                        f"Netzfrequenzmessung-Bot {version}\n"
                                        f"https://github.com/TheRedSpark/Netzfrequenzmessung")
    await context.bot.send_message(update.effective_user.id,
                                   text=f'Benutze /help um Hilfe mit den Befehlen und der Funktionsweise des Bots zu '
                                        'erhalten. \n')


async def netzfrequenz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    frequenz = netzfrequenz_pull()
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Die aktuelle Netzfrequenz beträgt: {frequenz}Hz")

async def mitmachen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(update.effective_user.id,
                                   text=f"https://github.com/TheRedSpark/Netzfrequenzmessung")
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Schau dir gerne das Repo an vielleicht möchtest du dich ja beteiligen.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(update.effective_user.id,
                                   text=f"Um einen guten Einstieg in das Thema zu erhalten empfehle ich dir diesen CC3 Talk\n")
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
