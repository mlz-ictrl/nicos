description = 'Generic configuration settings for NARZISS'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/narziss/'

KAFKA_BROKERS = ['localhost:9092']
