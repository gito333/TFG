from lancedb import DBConnection
from variables import CPV_LIST
from dbconnection import create_database_table, create_vector_table, drop_table
from datetime import datetime
from variables import *
import json, shutil, os

def get_cpv():
    with open(f"{CONFIG_LOCATION}config.json", "r") as json_file:
        try:
            data = json.load(json_file)
            for cpv in data['CPV']:
                CPV_LIST.append(cpv)
        except Exception:
            create_config_file()

def remove_db():
    with open(f"{CONFIG_LOCATION}config.json", "r+") as json_file:
        data = json.load(json_file)
        data['last_date_updated'] = ""
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()
    os.remove(f"{DB_LOCATION}licitaciones.db")
    if os.path.exists(f"{DB_LOCATION}lancedb"):
        print('holaa')
        shutil.rmtree(f"{DB_LOCATION}lancedb")

def ask_date():
    print("introduce el nuevo año desde el que te gustaría empezar entre 2022 y el actual")
    year = int(input())
    while (year < 2022 or year > int(datetime.now().year)):
        print("Introduce un año valido")
        year = int(input())
    print("introduce el nuevo mes desde el que te gustaría empezar")
    month = int(input())
    while (year == int(datetime.now().year) and (month > int(datetime.now().month)) or month < 1 ):
        print("Introduce un mes valido")
        month = int(input())
    while (month < 1 or month > 12):
        month = int(input())
    with open(f"{CONFIG_LOCATION}config.json", "r+") as json_file:
        data = json.load(json_file)
        data['last_date_updated'] = f"{year}-{month}-01T00:00:00.000000+0100"
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()

def restartdb():
    ask_date()
    create_database_table()
    create_vector_table()

def create_config_file():
    data = {
        "last_date_updated": "2022-01-01T00:00:00.000000+0100",
        "CPV": ["48"],
        "emails": "rodrigorincon324@gmail.com",
        "threads": 10
    }
    with open(f'{CONFIG_LOCATION}config.json', 'w+') as f:
        json.dump(data, f)
    ask_date()
    print("Creado el archivo de configuración")

def add_cpv():
    show_cpv()
    print("Introduce nuevo CPV")
    user_input = input()
    with open(f"{CONFIG_LOCATION}config.json", "r+") as json_file:
        data = json.load(json_file)
        if user_input not in data['CPV']:
            CPV_LIST.append(user_input)
            data['CPV'].append(user_input)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()

def remove_cpv():
    show_cpv()
    print("Introduce el CPV a eliminar")
    user_input = input()
    with open(f"{CONFIG_LOCATION}config.json", "r+") as json_file:
        data = json.load(json_file)
        if user_input in data['CPV']:
            data['CPV'].remove(user_input)
            CPV_LIST.remove(user_input)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()


def show_cpv():
    for cpv in CPV_LIST:
        print(cpv)

