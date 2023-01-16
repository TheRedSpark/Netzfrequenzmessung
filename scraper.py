import mysql.connector
import time
import requests
import random
from package import variables as v
import main

ort = main.ort


def data_insert(data):
    mydb = mysql.connector.connect(
        host=v.host(ort),
        user=v.user(ort),
        passwd=v.passwd(ort),
        database=v.database(),
        auth_plugin='mysql_native_password')

    my_cursor = mydb.cursor()
    time_sql = time.strftime("%Y-%m-%d %H:%M:%S")

    sql_maske = "INSERT INTO `Netzfrequenmessung`.`Data` (`Zeit`,`Frequenz`) VALUES (%s, %s); "
    data_n = (time_converter(data[0]),
              data[1])
    my_cursor.execute(sql_maske, data_n)
    mydb.commit()
    my_cursor.close()


def generate_url():
    client = round(random.randint(0, 100000) * 1) * 31
    url = f'https://netzfrequenzmessung.de:9081/frequenz02a.xml?c={client}'
    return url


def time_converter(time: str):
    time_split = time.split(" ")
    zeit = time_split[1]
    datum = time_split[0]
    datum_split = datum.split(".")
    time_converted = f'{datum_split[2]}.{datum_split[1]}.{datum_split[0]} {zeit}'
    return time_converted


def netzfrequenz_pull():
    response = requests.get(generate_url())
    print(generate_url())
    if response.status_code == 200:
        y = response.text.splitlines()
        netzfrequenz = y[1].replace("<f2>", "").replace("</f2>", "")
        zeit = y[3].replace("<z> ", "").replace("</z>", "")
        return [zeit, netzfrequenz]
    elif response.status_code == 426:
        raise ConnectionRefusedError
    else:
        print(response.status_code)
        raise ConnectionError


def main():
    try:
        data_insert(netzfrequenz_pull())
    except ConnectionRefusedError:
        print("Das war zu viel")
        time.sleep(1)


while True:
    main()
