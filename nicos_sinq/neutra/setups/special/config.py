description = 'Generic configuration settings for NEUTRA'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/neutra/'

KAFKA_BROKERS = ['localhost:9092']
