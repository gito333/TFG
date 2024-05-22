import os
import signal
import sys

from dbconnection import get_embeddings, connect_vector_db, get_from_db, create_vector_table, create_database_table
from licitacion import Licitacion
from parsing import update
from variables import *
from utils import *
from enums import search_querys, codigos_de_estado

def sigint_handler_main(sig, frame):
    print("Saludos")
    sys.exit(0)


def update_function():
    with open(f"{CONFIG_LOCATION}config.json", "r" )as json_file:
        data = json.load(json_file)
        if data['last_date_updated'] == "":
            restartdb()
    mailing = update()
    del(mailing)

def search_function():
    licitacion = Licitacion()
    try:
        print("Haz una busqueda semantica sobre lo que quieres buscar")
        user_input = input()
        embeddings = get_embeddings(user_input)
        tbl =  connect_vector_db()
        quantity = 0;
        while quantity > 100 or quantity < 1:
            print("introduce la cantidad de resultados que deseas")
            quantity = int(input())
        print("Quieres filtrar por campos? (y/n)")
        user_input = ""
        while (user_input != "y" and user_input != "n"):
            user_input = input()
        fecha = ""
        estado = ""
        if user_input == "y":
            while (user_input != "0"):
                print("0 siguiente")
                for i in search_querys:
                    print(i, search_querys.get(i))
                user_input = input()
                if (user_input == "1"):
                    print("introduce la fecha YYYY-MM-DD")
                    fecha = input()
                elif(user_input == "2"):
                    print("introduce el estado")
                    for i in codigos_de_estado:
                        print(i, codigos_de_estado.get(i))
                    estado = input()
        print("buscando")
        if estado != "" and fecha != "":
            res = tbl.search(embeddings).where(f"estado = '{estado}' AND fecha >= '{fecha}'", prefilter=True).limit(quantity).select(["Identificador", "Id_de_lote"]).to_list()
        elif (estado != ""):
            res = tbl.search(embeddings).where(f"estado = '{estado}'", prefilter=True).limit(quantity).select(["Identificador", "Id_de_lote"]).to_list()
        elif (fecha != ""):
            res = tbl.search(embeddings).where(f"fecha >= '{fecha}'", prefilter=True).limit(quantity).select(["Identificador", "Id_de_lote"]).to_list()
        else:
            res = tbl.search(embeddings).limit(quantity).select(["Identificador", "Id_de_lote"]).to_list()
        for i in res:
            x = get_from_db(i["Identificador"], i["Id_de_lote"])
            for n,key in enumerate(licitacion.__dict__.keys()):
                print(f"\033[94m{key}: \033[92m{x[n]}\033[0m")
            print()
        print("busqueda terminada")
    except Exception as e:
        print(f"no existe la base de datos {e}")

def main():
    signal.signal(signal.SIGINT, sigint_handler_main)
    os.makedirs(DB_LOCATION, exist_ok=True)
    os.makedirs(CONFIG_LOCATION, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(f'{CONFIG_LOCATION}config.json'):
        create_config_file()
    get_cpv()
    if not os.path.exists(f"{DB_LOCATION}licitaciones.db"):
        create_database_table()
    if not os.path.exists(f"{DB_LOCATION}lancedb"):
        create_vector_table()
    while True:
        print("elige entre search, updatedb, removedb, addcpv, removecpv, showcpv")
        user_input = input()
        if user_input == "updatedb":
            update_function()
        elif user_input == "search":
            search_function()
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

