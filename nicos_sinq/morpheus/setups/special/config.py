description = 'Generic configuration settings for MORPHEUS'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/morpheus/'

KAFKA_BROKERS = ['localhost:9092']
