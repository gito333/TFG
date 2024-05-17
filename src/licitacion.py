from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Licitacion:
    Identificador: str
    Link_licitacion: str
    Fecha_actualizacion: str
    Estado: str
    Primera_publicacion: str
    Numero_expediente: str
    Objeto_del_Contrato: str
    Presupuesto_base_sin_impuestos: str
    Cpv: list[str]
    Id_de_lote: str
    Tipo_de_contrato: str
    Lugar_de_ejecucion: str
    Organo_de_Contratacion: str
    Tipo_de_Administracion: str
    Tipo_de_procedimiento: str 
    Sistema_de_contratacion:  str
    Fecha_de_presentacion_de_ofertas:  str
    Objeto_licitacion_lote:  str
    Presupuesto_base_sin_impuestos_licitacion_lote:  str
    Resultado_licitacion_lote:  str
    Numero_de_ofertas_recibidas_por_licitacion_lote:  str
    Adjudicatario_licitacion_lote:  str
    Importe_adjudicacion_sin_impuestos_licitacion_lote:  str
    
    def __init__(
            self,
            Identificador:  str = "",
            Link_licitacion:  str = "",
            Fecha_actualizacion:  str = "",
            Estado:  str = "",
            Primera_publicacion: str = "",
            Numero_expediente:  str = "",
            Objeto_del_Contrato:  str = "",
            Presupuesto_base_sin_impuestos:  str = "",
            Cpv: list[str] = [],
            Id_de_lote:  str = "",
            Tipo_de_contrato:  str = "",
            Lugar_de_ejecucion:  str = "",
            Organo_de_Contratacion:  str = "",
            Tipo_de_Administracion:  str = "",
            Tipo_de_procedimiento:  str = "",
            Sistema_de_contratacion:  str = "",
            Fecha_de_presentacion_de_ofertas:  str = "",
            Objeto_licitacion_lote:  str = "",
            Presupuesto_base_sin_impuestos_licitacion_lote:  str = "",
            Resultado_licitacion_lote:  str = "",
            Numero_de_ofertas_recibidas_por_licitacion_lote:  str = "",
            Adjudicatario_licitacion_lote:  str = "",
            Importe_adjudicacion_sin_impuestos_licitacion_lote:  str = "",
        ):
            self.Identificador = Identificador
            self.Link_licitacion = Link_licitacion
            self.Fecha_actualizacion = Fecha_actualizacion
            self.Estado = Estado
            self.Primera_publicacion = Primera_publicacion
            self.Numero_expediente = Numero_expediente
            self.Objeto_del_Contrato = Objeto_del_Contrato
            self.Presupuesto_base_sin_impuestos = Presupuesto_base_sin_impuestos
            self.Cpv = Cpv
            self.Id_de_lote = Id_de_lote
            self.Tipo_de_contrato = Tipo_de_contrato
            self.Lugar_de_ejecucion = Lugar_de_ejecucion
            self.Organo_de_Contratacion = Organo_de_Contratacion
            self.Tipo_de_Administracion = Tipo_de_Administracion
            self.Tipo_de_procedimiento = Tipo_de_procedimiento
            self.Sistema_de_contratacion = Sistema_de_contratacion
            self.Fecha_de_presentacion_de_ofertas = Fecha_de_presentacion_de_ofertas
            self.Objeto_licitacion_lote = Objeto_licitacion_lote
            self.Presupuesto_base_sin_impuestos_licitacion_lote = Presupuesto_base_sin_impuestos_licitacion_lote
            self.Resultado_licitacion_lote = Resultado_licitacion_lote
            self.Numero_de_ofertas_recibidas_por_licitacion_lote = Numero_de_ofertas_recibidas_por_licitacion_lote
            self.Adjudicatario_licitacion_lote = Adjudicatario_licitacion_lote
            self.Importe_adjudicacion_sin_impuestos_licitacion_lote = Importe_adjudicacion_sin_impuestos_licitacion_lote

    def __str__(self):
        attributes = vars(self)
        result = ""
        for attr, value in attributes.items():
            result += f"{attr}: {value}\n"
        return result    

