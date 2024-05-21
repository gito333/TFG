import os
import signal
import sys
import src.dbconnection as dbconnection
from utils import *


def sigint_handler_main(sig, frame):
    print("adios")
    sys.exit(0)

def sigint_handler_function(sig, frame):
    main()

def main():
    signal.signal(signal.SIGINT, sigint_handler_main)
    if not os.path.exists(f'{CONFIG_LOCATION}config.json'):
        create_config_file()
    get_cpv()
    if not os.path.exists(f"{DB_LOCATION}licitaciones.db"):
        dbconnection.create_database_table()
    if not os.path.exists(f"{DB_LOCATION}lancedb"):
        dbconnection.create_vector_table()
    while True:
        signal.signal(signal.SIGINT, sigint_handler_main)
        print("elige entre search, updatedb, removedb, addcpv, removecpv, showcpv")
        user_input = input()
        signal.signal(signal.SIGINT, sigint_handler_function)
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

