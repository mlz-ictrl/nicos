description = 'Generic configuration settings for SANS'
import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']
#HISTOGRAM_MEMORY_URL = 'http://localhost:8080/admin'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/orion/'
