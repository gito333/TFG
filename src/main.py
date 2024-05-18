import json
import os
from datetime import datetime
import shutil
import parsing
import connectionSQL
from licitacion import Licitacion
from variables import CPV_LIST

def remove_db():
    with open("config.json", "r+") as json_file:
        data = json.load(json_file)
        data['last_date_updated'] = ""
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()
    connectionSQL.drop_table()
    if os.path.exists('lancedb'):
        shutil.rmtree('lancedb')

def restartdb():
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
    with open("config.json", "r+") as json_file:
        data = json.load(json_file)
        data['last_date_updated'] = f"{year}-{month}-01T00:00:00.000000+0100"
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()
    connectionSQL.create_database_table()
    connectionSQL.create_vector_table()

def create_config_file():
    data = {
        "last_date_updated": "2022-01-01T00:00:00.000000+0100",
        "CPV": ["48", "30", "72", "50", "51", "64"],
        "emails": "",
        "threads": 10
    }
    with open('config.json', 'w') as f:
        json.dump(data, f)
        print("Creado el archivo de configuración")

def add_cpv():
    show_cpv()
    print("Introduce nuevo CPV")
    user_input = input()
    with open("config.json", "r+") as json_file:
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
    with open("config.json", "r+") as json_file:
        data = json.load(json_file)
        if user_input in data['CPV']:
            data['CPV'].remove(user_input)
            CPV_LIST.remove(user_input)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()

def get_cpv():
    with open("config.json", "r") as json_file:
        try:
            data = json.load(json_file)
            for cpv in data['CPV']:
                CPV_LIST.append(cpv)
        except Exception:
            create_config_file()

def show_cpv():
    for cpv in CPV_LIST:
        print(cpv)

def main():
    if not os.path.exists('config.json'):
        create_config_file()
    get_cpv()
    if not os.path.exists("licitaciones.db"):
        connectionSQL.create_database_table()
    if not os.path.exists("lancedb"):
        connectionSQL.create_vector_table()
    licitacion = Licitacion()
    while True:
        print("elige entre search, updatedb, removedb, addcpv, removecpv, showcpv")
        user_input = input()
        if user_input == "updatedb":
            with open("config.json", "r" )as json_file:
                data = json.load(json_file)
                if data['last_date_updated'] == "":
                    restartdb()
            mailing = parsing.update()
            del(mailing)
        elif user_input == "search":
            try:
                print("Haz una busqueda semantica sobre lo que quieres buscar")
                user_input = input()
                embeddings = connectionSQL.get_embeddings(user_input)
                tlb =  connectionSQL.connect_vector_db()
                res = tlb.search(embeddings).limit(4).select(["Identificador", "Id_de_lote"]).to_list()
                for i in res:
                    print(f"identificador {i['Identificador']} id de lote {i['Id_de_lote']}")
                    x = connectionSQL.get_from_db(i["Identificador"], i["Id_de_lote"])
                    for n,key in enumerate(licitacion.__dict__.keys()):
                        print(f"{key}: {x[n]}")

            except Exception as e:
                print(f"no existe la base de datos {e}")
        elif user_input == "removedb":
            remove_db()
            print("la bbdd ha sido eliminada")
        elif user_input == "addcpv":
            add_cpv()
            print("cpv añadido")
        elif user_input == "removecpv":
            remove_cpv()
            print("cpv eliminado")
        elif user_input == "showcpv":
            show_cpv()

if __name__ == "__main__":
    main()

