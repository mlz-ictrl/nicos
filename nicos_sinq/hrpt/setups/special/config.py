description = 'Generic configuration settings for HRPT'

import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']
#HISTOGRAM_MEMORY_URL = 'http://localhost:8080/admin'
HISTOGRAM_MEMORY_URL = os.environ.get('HRPTHM', 'http://localhost:8080/admin')
#HISTOGRAM_MEMORY_ENDIANESS = 'little'
HISTOGRAM_MEMORY_ENDIANESS = 'big'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/hrpt/'
