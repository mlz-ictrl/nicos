description = 'Generic configuration settings for EIGER'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/eiger/'

KAFKA_BROKERS = ['localhost:9092']
