description = 'Generic configuration settings for SINQTEST'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/sinqtest/'

KAFKA_BROKERS = ['localhost:9092']
