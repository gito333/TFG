import sqlite3, lancedb, pyarrow as pa
import licitacion
from variables import CPV_LIST,DB_LOCATION
from sentence_transformers import SentenceTransformer

def connect_vector_db():
    uri = f"{DB_LOCATION}lancedb"
    db = lancedb.connect(uri)
    return db.open_table("licitaciones")


def create_vector_table():
    uri = "{DB_LOCATION}lancedb"
    db = lancedb.connect(uri)
    schema = pa.schema([pa.field("vector", pa.list_(pa.float32(), list_size=384)),
                        pa.field("Identificador", pa.string()),
                        pa.field("Id_de_lote", pa.string())])
    db.create_table("licitaciones", schema=schema)

def create_database_table():
    open(f"{DB_LOCATION}licitaciones.db", "x")
    conn = sqlite3.connect(f'{DB_LOCATION}licitaciones.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS licitaciones (
                Identificador TEXT,
                Link_licitacion TEXT,
                Fecha_actualizacion TEXT,
                Estado TEXT,
                Primera_publicacion TEXT,
                Numero_expediente TEXT,
                Objeto_del_Contrato TEXT,
                Presupuesto_base_sin_impuestos TEXT,
                Cpv TEXT,
                Id_de_lote TEXT,
                Numero_de_lotes INTEGER,
                Tipo_de_contrato TEXT,
                Lugar_de_ejecucion TEXT,
                Organo_de_Contratacion TEXT,
                Tipo_de_Administracion TEXT,
                Tipo_de_procedimiento TEXT,
                Sistema_de_contratacion TEXT,
                Fecha_de_presentacion_de_ofertas TEXT,
                Objeto_licitacion_lote TEXT,
                Presupuesto_base_sin_impuestos_licitacion_lote TEXT,
                Resultado_licitacion_lote TEXT,
                Numero_de_ofertas_recibidas_por_licitacion_lote TEXT,
                Adjudicatario_licitacion_lote TEXT,
                Importe_adjudicacion_sin_impuestos_licitacion_lote TEXT,
                PRIMARY KEY (Identificador, Id_de_lote)
                )''')
    conn.commit()
    conn.close()

def drop_table():
    conn = sqlite3.connect(f'{DB_LOCATION}licitaciones.db')
    cursor = conn.cursor()
    cursor.execute(''' DROP TABLE IF EXISTS licitaciones ''')
    conn.commit()
    conn.close()

def get_from_db(Identificador: str, Id_de_lote: str):
    conn = sqlite3.connect(f'{DB_LOCATION}licitaciones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM licitaciones WHERE Identificador = ? AND Id_de_lote = ?", (Identificador, Id_de_lote))
    data = cursor.fetchone()
    conn.commit()
    cursor.close()
    return data

def search_actualization_db(Identificador: str, Id_de_lote: str):
    conn = sqlite3.connect(f'{DB_LOCATION}licitaciones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Fecha_actualizacion FROM licitaciones WHERE Identificador = ? AND Id_de_lote = ?", (Identificador, Id_de_lote))
    data = cursor.fetchone()
    conn.commit()
    cursor.close()
    if data:
        return data[0]
    return data
    
def insert_licitacion(licitacion: licitacion.Licitacion):
    conn = sqlite3.connect(f'{DB_LOCATION}licitaciones.db')
    cursor = conn.cursor()
    modified = False
    previous_time = search_actualization_db(licitacion.Identificador, licitacion.Id_de_lote)
    update_time = licitacion.Fecha_actualizacion
    if previous_time and previous_time < update_time:
        print(f"updating {licitacion.Identificador} lote {licitacion.Id_de_lote}")
        sql = f'''UPDATE licitaciones SET {', '.join([x +' = ?' for x in licitacion.__dict__.keys()])}
                WHERE Identificador = ? AND Id_de_lote = ?'''
        values = [y.__str__() for _,y in licitacion.__dict__.items()]
        values.append(licitacion.Identificador)
        values.append(licitacion.Id_de_lote)
        cursor.execute(sql, values)
    elif previous_time and previous_time >= update_time:
        pass
    else:
        found = False
        for element in CPV_LIST:
            for cpv in licitacion.Cpv:
                if(cpv.startswith(element,0)):
                    if licitacion.Id_de_lote == "0":
                        print(f"insertando {licitacion.Identificador} \n{licitacion.Objeto_del_Contrato}")
                        insert_vector(licitacion.Objeto_del_Contrato, licitacion.Identificador, licitacion.Id_de_lote)
                    elif licitacion.Id_de_lote > "0":
                        print(f"insertando {licitacion.Identificador} lote {licitacion.Id_de_lote} \n{licitacion.Objeto_licitacion_lote}")
                        insert_vector(licitacion.Objeto_licitacion_lote, licitacion.Identificador, licitacion.Id_de_lote)
                    sql = f'''INSERT INTO licitaciones ({', '.join(licitacion.__dict__.keys())})
                            VALUES ({', '.join(['?' for _ in licitacion.__dict__.keys()])})'''
                    values = [y.__str__() for _,y in licitacion.__dict__.items()]
                    cursor.execute(sql, values)
                    found = True
                    modified = True
                    break
            if found:
                break
    conn.commit()
    conn.close()
    return modified

def insert_vector(text: str, Identificador: str, Id_de_lote: str):
    embeddings = get_embeddings(text)
    tbl = connect_vector_db()
    tbl.add([{"vector": embeddings, "Identificador":Identificador,"Id_de_lote":Id_de_lote}])

def get_embeddings(text:str):
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', token='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') 
    embeddings = model.encode(text)
    return embeddings
