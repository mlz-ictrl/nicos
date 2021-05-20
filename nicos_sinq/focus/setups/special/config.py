description = 'Generic configuration settings for FOCUS'
import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']

UPPERHM_MEMORY_URL = os.environ.get(
    'FOCUSUPPERHM', 'http://localhost:9080/admin'
)
MIDDLEHM_MEMORY_URL = os.environ.get(
    'FOCUSMIDDLEHM', 'http://localhost:9070/admin'
)
LOWERHM_MEMORY_URL = os.environ.get(
    'FOCUSLOWERHM', 'http://localhost:9060/admin'
)
F2DH_MEMORY_URL = os.environ.get('FOCUS2DHM', 'http://localhost:9050/admin')

HISTOGRAM_MEMORY_ENDIANESS = 'big'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/focus/'
