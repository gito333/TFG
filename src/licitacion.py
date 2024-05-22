from dataclasses import dataclass, field
@dataclass
class Licitacion:
    Identificador: str = "" 
    Link_licitacion: str = ""
    Fecha_actualizacion: str = ""
    Estado: str = ""
    Primera_publicacion: str = ""
    Numero_expediente: str = ""
    Objeto_del_Contrato: str = ""
    Presupuesto_base_sin_impuestos: str = ""
    Cpv: list[str] = field(default_factory=list)
    Id_de_lote: str = ""
    Tipo_de_contrato: str = ""
    Lugar_de_ejecucion: str = ""
    Organo_de_Contratacion: str = ""
    Tipo_de_Administracion: str = ""
    Tipo_de_procedimiento: str = ""
    Sistema_de_contratacion: str = ""
    Fecha_de_presentacion_de_ofertas: str = ""
    Objeto_licitacion_lote: str = ""
    Presupuesto_base_sin_impuestos_licitacion_lote: str = ""
    Resultado_licitacion_lote: str = ""
    Numero_de_ofertas_recibidas_por_licitacion_lote: str = ""
    Adjudicatario_licitacion_lote: str = ""
    Importe_adjudicacion_sin_impuestos_licitacion_lote: str = ""

    def __str__(self):
        attributes = vars(self)
        result = ""
        for attr, value in attributes.items():
            result += f"{attr}: {value} \n"
        return result

    def show_in_terminal(self):
        attributes = vars(self)
        result = ""
        for attr, value in attributes.items():
            result += f"\033[94m{attr}: \033[92m{value}\033[0m\n"
        return result
    
