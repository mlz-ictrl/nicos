description = 'Generic configuration settings for DMC'

import os

group = 'configdata'

KAFKA_BROKERS = ['ess01.psi.ch:9092']
#KAFKA_BROKERS = ['localhost:9092']

HISTOGRAM_MEMORY_URL = 'http://dmchm:80/admin'
HISTOGRAM_MEMORY_ENDIANESS = 'little'

CACHE_COLLECTOR_TOPIC = 'DMC_nicosCache'

JUST_BIN_IT_COMMANDS_TOPIC = 'DMC_histCommands'
JUST_BIN_IT_RESPONSES_TOPIC = 'DMC_histResponse'
JUST_BIN_IT_HISTOGRAMS_TOPIC = 'DMC_histograms'
JUST_BIN_IT_DATA_TOPIC = 'DMC_detector'

FORWARDER_STATUS_TOPIC = 'DMC_forwarderStatus'

FILEWRITER_COMMAND_TOPIC = 'DMC_filewriterConfig'
FILEWRITER_STATUS_TOPIC = 'DMC_filewriterStatus'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/dmc/'
