description = 'Generic configuration settings for TASP'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/tasp/'

KAFKA_BROKERS = ['localhost:9092']
