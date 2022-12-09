description = 'Generic configuration settings for SANS-LLB'
import os

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/sans-llb/'
