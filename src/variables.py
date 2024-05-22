from os import getenv
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
CPV_LIST = []
DATA_FOLDER = f"{getenv('HOME')}/licitaciones-app/data/"
DB_LOCATION = f"{getenv('HOME')}/licitaciones-app/var/"
CONFIG_LOCATION = f"{getenv('HOME')}/licitaciones-app/etc/"
NAMESPACES = {'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
              'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
              'cac-place-ext':'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2',
              'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2'}
URLS =        [("https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_", "licitacionesPerfilesContratanteCompleto3.atom")]
