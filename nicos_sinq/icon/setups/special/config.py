description = 'Generic configuration settings for BOA'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/icon/'

KAFKA_BROKERS = ['localhost:9092']
