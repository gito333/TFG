resultados_de_procedimiento = {
    "1": "Adjudicado Provisionalmente",
    "2": "Adjudicado Definitivamente",
    "3": "Desierto",
    "4": "Desistimiento",
    "5": "Renuncia",
    "6": "Desierto Provisionalmente",
    "7": "Desierto Definitivamente",
    "8": "Adjudicado",
    "9": "Formalizado",
    "10": "Licitador mejor valorado:Requerimiento de documentacion",
    "null": "null"
}
sistemas_de_contratacion = {
    "0": "No aplica",
    "1": "Establecimiento del Acuerdo Marco",
    "2": "Establecimiento del Sistema Dinámico de Adquisición",
    "3": "Contrato basado en un Acuerdo Marco",
    "4": "Contrato basado en un Sistema Dinámico de Adquisición",
    "null": "null"
}
tipos_de_procedimiento = {
    "1": "Abierto",
    "2": "Restringido",
    "3": "Negociado sin publicidad",
    "4": "Negociado con publicidad",
    "5": "Diálogo competitivo",
    "6": "Contrato Menor",
    "7": "Derivado de acuerdo marco",
    "8": "Concurso de proyectos",
    "100": "Normas internas",
    "999": "Otros",
    "null": "null"
}
codigos_de_estado = {
    "RES": "Resuelta",
    "ADJ": "Adjudicada",
    "PUB": "En plazo", 
    "PRE": "Anuncio Previo",
    "ANUL": "Anulada",
    "EV": "Pendiente de adjudicacion",
    "null": "null"
}
tipos_de_contrato = {
    "1": "Suministros",
    "2": "Servicios",
    "3": "Obras",
    "21": "Gestión de Servicios Públicos",
    "31": "Concesión de Obras Públicas",
    "40": "Colaboración entre el sector público y sector privado",
    "7": "Administrativo especial",
    "8": "Privado",
    "50": "Patrimonial",
    "999": "Otros",
    "null": "null"
}
tipos_de_anuncio = {
    "DOC_PIN": "Anuncio Previo",
    "DOC_CN": "Anuncio de Licitación",
    "DOC_CD": "Anuncio de Pliegos",
    "DOC_DD": "Anuncio de Documento Descriptivo",
    "DOC_CAN_PROV": "Anuncio de Adjudicación Provisional",
    "DOC_CAN_DEF": "Anuncio de Adjudicación Definitiva",
    "DOC_CAN_ADJ": "Anuncio de Adjudicación",
    "DOC_FORM": "Anuncio de Formalización",
    "RENUNCIA": "Anuncio de Renuncia",
    "DESISTIMIENTO": "Anuncio de Desistimiento",
    "ANUL_PIN": "Anulación de Anuncio Previo",
    "ANUL_CN": "Anulación de Anuncio de Licitación",
    "ANUL_CD": "Anulación de Anuncio de Pliegos",
    "ANUL_DD": "Anulación de Anuncio de Documento Descriptivo",
    "ANUL_CAN_ADJ": "Anulación de Anuncio de Adjudicación",
    "ANUL_FORM": "Anulación de Anuncio de Formalización",
    "ANUL_RENUNCIA": "Anulación de Anuncio de Renuncia",
    "ANUL_DESISTIMIENTO": "Anulación de Anuncio de Desistimiento"
}

class Element_mock():
    def __init__(self, string: str) -> None:
        self.string = string
        self.attrib = {'href': 'null'}

    def text(self):
        return self.string
        
    
