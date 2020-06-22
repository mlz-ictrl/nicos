description = 'Generic configuration settings for DMC'

import os

group = 'configdata'

#KAFKA_BROKERS = ['ess01:9092']
KAFKA_BROKERS = ['localhost:9092']
HISTOGRAM_MEMORY_URL = 'http://dmchm:80/admin'
HISTOGRAM_MEMORY_ENDIANESS = 'little'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/dmc/'
