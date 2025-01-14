description = 'Generic configuration settings for POLDI'
# Based hrpt

import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']
#HISTOGRAM_MEMORY_URL = 'http://localhost:8080/admin'
#HISTOGRAM_MEMORY_URL = os.environ.get('POLDIHM', 'http://localhost:8080/admin')
HISTOGRAM_MEMORY_URL = os.environ.get('POLDIHM', 'http://poldihm:80/admin')
#HISTOGRAM_MEMORY_ENDIANESS = 'little'
HISTOGRAM_MEMORY_ENDIANESS = 'big'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/poldi/'
