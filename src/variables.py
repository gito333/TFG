DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
CPV_LIST = []
DATA_FOLDER = "/tmp/licitaciones-app/data/"
DB_LOCATION = "/var/licitaciones-app/"
CONFIG_LOCATION = "/etc/licitaciones-app/"
NAMESPACES = {'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
              'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
              'cac-place-ext':'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2',
              'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2'}
URLS = [("https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_1044/PlataformasAgregadasSinMenores_", "licitacionesPerfilesContratanteCompleto3.atom"),
        ("https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_", "PlataformasAgregadasSinMenores.atom")]