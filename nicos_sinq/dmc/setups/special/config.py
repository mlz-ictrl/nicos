description = 'Generic configuration settings for DMC'

import os

group = 'configdata'

KAFKA_BROKERS = ['linkafka01.psi.ch:9092']

JUST_BIN_IT_COMMANDS_TOPIC = 'DMC_histCommands'
JUST_BIN_IT_RESPONSES_TOPIC = 'DMC_histResponse'
JUST_BIN_IT_HISTOGRAMS_TOPIC = 'DMC_histograms'
JUST_BIN_IT_DATA_TOPIC = 'DMC_detector'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/dmc/'
