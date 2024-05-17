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
    "null": "null",
    "10": "Licitador mejor valorado:Requerimiento de documentacion"
}
sistemas_de_contratacion = {
    "0": "No aplica",
    "1": "Establecimiento del Acuerdo Marco",
    "2": "Establecimiento del Sistema Dinámico de Adquisición",
    "3": "Contrato basado en un Acuerdo Marco",
    "null": "null",
    "4": "Contrato basado en un Sistema Dinámico de Adquisición"
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
    "null": "null",
    "999": "Otros"
}
codigos_de_estado = {
    "RES": "Resuelta",
    "ADJ": "Adjudicada",
    "PUB": "En plazo", 
    "PRE": "Anuncio Previo",
    "ANUL": "Anulada",
    "EV": "Evaluada",
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
    "null": "null",
    "999": "Otros"
}

class Element_mock():
    def __init__(self, string: str) -> None:
        self.string = string
        self.attrib = {'href': 'null'}

    def text(self):
        return self.string
        
    
