description = 'Generic configuration settings for CAMEA'
import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']
#HISTOGRAM_MEMORY_URL = 'http://localhost:8080/admin'
HISTOGRAM_MEMORY_URL = os.environ.get('CAMEAHM', 'http://localhost:8080/admin')
HISTOGRAM_MEMORY_ENDIANESS = 'little'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/camea/'
