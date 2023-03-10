import time
import mysql.connector  # 8.0.28
import requests
import random
# import math as Math
from package import variables as v
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup  # 20.0a1
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, \
    filters, ConversationHandler  # 20.0a1

on_server = False
version = "1.1"
is_live = False
ort = "server"
netz_alert = 0
freqenz_state = 2

frequenz_regeln = [
    # [Netzfrequenz ,"Erklärung des Zustandes"],
    [52.00, f'Oberhalb dieser Schwelle beginnt im europäischen Netzverbund ein unzulässiger Betriebszustand. '
            f'Netzersatzanlagen steuern diesen Wert gezielt an, um andere Erzeuger (pv etc.) zu deaktivieren.'
            f'Bei weiterer Frequenzsteigerung wird ein gezielter Blackout ausgelöst'],

    [51.50, f'Alle regelbaren Kraftwerke sollten an diesem punkt die Stromerzeugung komplett eingestellt haben.'
            f'Dies beinhaltet auch Windräder, PV-Anlagen und Gaskraftwerke'],

    [51.00, f'Von 51,00 Hz bis 51,50 Hz müssen neue Kraftwerke mindestens 90 Minuten lauffähig bleiben. '
            f'Ältere Kraftwerke wie unregelbare PV-Anlagen gehen ab hier bereits vom Netz.'],

    [50.50,
     f'Obere Grenze der im Normalbetrieb geduldeten Frequenzabweichungen. Netz-ersatzanlagen halten die Frequenz '
     f'bei 50,5 bis 51 Hz.'],

    [50.20, f'von 50,20 Hz bis 51,5 Hz sollen regelbare Erzeugungsanlagen (pv, BHKW, etc.) eine frequenzbasierte '
            f'leistungsreduktion vornehmen. Damit sezut die Sekundärregelung Pumpspeicherkraftwerke steigern'
            f' die Speicherleistung und Gaskraftwerke drosseln die Einspeißung. '
            f'Sollte die Überproduktion länger als 15 min anhalten werden Kernkraftwerke '
            f'gedrosselt.'],

    [50.00,
     f'Wir befinden uns auf dem Band von 49,5 bis 50,5 Hz. Die Grundfrequenz des Stromnetzes beträgt 50 Hz damit'
     f' befinden wir uns im Normalbetrieb.'],

    [49.80,
     f'Stufe 1 der Netzstabilisierung. Der ÜNB kann die Aktivierung von zusätzlicher Erzeugungsleistung anweisen.'],

    [49.50, f'Untere Grenze der im Normalbetrieb geduldeten Frequenzabweichungen wurde erreicht.'],

    [49.00, f'Stufe 2 der Netzstabilisierung aktiviert frequenzabhängigen lastabwurf von 10 bis 15% der verbraucher'
            f' (gezielter “Teil-Blackout).'],

    [48.70, f'Stufe 3 der Netzstabilisierung. Abermals frequenzabhängiger lastabwurf von weiteren 10 bis 15% der '
            f'Verbraucher.'],

    [48.40, f'Stufe 4 der Netzstabilisierung. Frequenzabhängiger Lastabwurf. Weitere 10 bis 15% der Verbraucher gehen '
            f'vom Netz.'],

    [47.50, f'Stufe 5 der Netzstabilisierung führt zur gezielten Abtrennung von Netzsegmenten und Kraftwerken.'
            f' “Regionaler Blackout”'],

    [47.00, f'Unterhalb dieser Schwelle beginnt im europäischen Netzverbund ein unzulässiger Betriebszustand.'],

]

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


def generate_url():
    client = round(random.randint(0, 10) * 10000) * 31
    url = f'https://netzfrequenzmessung.de:9081/frequenz02a.xml?c={client}'
    return url


def netzfrequenz_pull():
    response = requests.get(generate_url())
    time.sleep(1)
    if response.status_code == 200:
        y = response.text.splitlines()
        netzfrequenz = y[1].replace("<f2>", "").replace("</f2>", "")
        zeit = y[3].replace("<z> ", "").replace("</z>", "")
        return [zeit, netzfrequenz]
    elif response.status_code == 429:
        raise ConnectionRefusedError
    else:
        print(response.status_code)
        raise ConnectionError


def get_netzdata(number_of_data) -> list:
    mydb = mysql.connector.connect(
        host=v.host(ort),
        user=v.user(ort),
        passwd=v.passwd(ort),
        database=v.database(),
        auth_plugin='mysql_native_password')

    my_cursor = mydb.cursor()
    my_cursor.execute(f'SELECT * FROM `Netzfrequenmessung`.`Data` ORDER BY Zeit desc limit {number_of_data}')
    result = my_cursor.fetchall()
    return result


def freqenz_analyse(frequenz, frequenz_state):
    while True:
        if float(frequenz_regeln[frequenz_state - 1][0]) > float(frequenz) > float(
                frequenz_regeln[frequenz_state + 1][0]):
            break
        elif float(frequenz_regeln[frequenz_state - 1][0]) > float(
                frequenz):  # Frequenzbereich liegt unter dem alten Wert
            frequenz_state = frequenz_state + 1
        elif float(frequenz) > float(
                frequenz_regeln[frequenz_state + 1][0]):  # Frequenzbereich liegt über dem alten Wert
            print("Frequenz ist drüber")
            frequenz_state = frequenz_state - 1
        else:
            print("Nicht im If statment")

    return frequenz_state

def get_users():
    results_clean = []
    mydb = mysql.connector.connect(
        host=v.host(ort),
        user=v.user(ort),
        passwd=v.passwd(ort),
        database=v.database(),
        auth_plugin='mysql_native_password')

    my_cursor = mydb.cursor()
    my_cursor.execute(f"SELECT User_Id FROM `Netzfrequenmessung`.`Users` ")
    results_raw = my_cursor.fetchall()
    my_cursor.close()
    for raw in results_raw:
        clen = int(str(raw).replace("(", "").replace(",)", "").strip())
        results_clean.append(clen)
    return results_clean

def pre_main() -> int:
    if 50.20 > float(get_netzdata(1)[0][1]) > 49.80:
        print("Netzfrequenz ist im Normalbereich")
        freqenz_state = 5
        return freqenz_state

    else:
        return freqenz_analyse(float(get_netzdata(1)[0][1]), 1)


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
                                        'erhalten. \n'
                                        'Benutze /info oder /i um Infos über die Netzfrequenz zu erhalten\n'
                                        'Benutze /netzfrequenz oder /f um dir die aktuelle Netzfrequenz anzuzeigen zu lassen \n'
                                        'Benutze /mitmachen um den Quellcode und Zugang zum Repo auf Github zu erhalten\n')


async def netzfrequenz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userlogging(update.effective_user.id, update.effective_user.username, update.effective_message.chat_id,
                update.effective_message.text_markdown, update.effective_message.id, update.effective_user.first_name,
                update.effective_user.last_name, update.effective_user.language_code)
    try:
        await context.bot.send_message(update.effective_user.id,
                                       text=f"Die aktuelle Netzfrequenz beträgt {netzfrequenz_pull()[1]} Hz\n"
                                            f"Die Messung wurde um {netzfrequenz_pull()[0]} Uhr durchgeführt")
    except ConnectionRefusedError:
        await context.bot.send_message(update.effective_user.id,
                                       text=f"Die aktuelle Netzfrequenz beträgt {get_netzdata(1)[0][1]} Hz\n"
                                            f"Die Messung wurde um {get_netzdata(1)[0][0]} Uhr durchgeführt\n"
                                            f"Die Messung wurde nicht durchgeführt, da die maximale Anzahl an Anfragen "
                                            f"erreicht wurde. \n")
    except ConnectionError:
        await context.bot.send_message(update.effective_user.id,
                                       text=f"Die aktuelle Netzfrequenz beträgt {get_netzdata(1)[0][1]} Hz\n"
                                            f"Die Messung wurde um {get_netzdata(1)[0][0]} Uhr durchgeführt\n"
                                            f"Die Messung wurde nicht durchgeführt, da ein Fehler aufgetreten ist. \n")
    except Exception as e:
        await context.bot.send_message(update.effective_user.id,
                                       text=f"Die aktuelle Netzfrequenz beträgt {get_netzdata(1)[0][1]} Hz\n"
                                            f"Die Messung wurde um {get_netzdata(1)[0][0]} Uhr durchgeführt\n"
                                            f"Die Messung wurde nicht durchgeführt, da ein Fehler aufgetreten ist. \n"
                                            f"Error: {e}")


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


async def alert_freq(context: ContextTypes.DEFAULT_TYPE) -> None:
    freqenz_state = pre_main()
    global anzahl_0
    if freqenz_state != 5:
        if not is_live:
            anzahl = [v.telegram_user_id]
            for t_user in anzahl:
                try:
                    await context.bot.send_message(t_user, text=f'Der aktuelle stand ist {freqenz_state}')
                    await context.bot.send_message(t_user, text=f'{frequenz_regeln[freqenz_state][1]}')
                except:
                    print(f'Fehlgeschlagen für User: {t_user}')
        elif is_live:
            anzahl = get_users()
            for t_user in anzahl:
                try:
                    await context.bot.send_message(t_user, text=f'{freqenz_state[freqenz_state][1]}')
                    print(f'Update:Erfolg für User: {t_user}')
                    await context.bot.send_message(v.telegram_user_id, text=f'Push fertig für {len(anzahl)} User')
                except:
                    print(f'Fehlgeschlagen für User: {t_user}')


def main() -> None:
    # Creating a telegram bot.
    application = Application.builder().token(v.telegram_netzfrequenz_api(is_live)).build()
    pre_main()
    # Adding the handlers for the commands.
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler(["netzfrequenz", "f"], netzfrequenz))
    application.add_handler(CommandHandler(["info", "i"], info))
    application.add_handler(CommandHandler("mitmachen", mitmachen))
    job_queue = application.job_queue

    # Running the function send_push every 60 seconds * 60 minutes * stundenabstand_push.
    job_queue.run_repeating(alert_freq, interval=5, first=5)
    application.run_polling(1)


if __name__ == '__main__':
    main()
