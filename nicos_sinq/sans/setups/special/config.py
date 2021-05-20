description = 'Generic configuration settings for SANS'
import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']
#HISTOGRAM_MEMORY_URL = 'http://localhost:8080/admin'
HISTOGRAM_MEMORY_URL = os.environ.get('SANSHM', 'http://localhost:8080/admin')
HISTOGRAM_MEMORY_ENDIANESS = 'big'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/sans/'
