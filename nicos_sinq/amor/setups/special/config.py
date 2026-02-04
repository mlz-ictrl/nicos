description = 'Generic configuration settings for AMOR'
import os

group = 'configdata'

KAFKA_BROKERS = [os.environ.get('KAFKABROKERS', 'linkafka01.psi.ch:9092')]

FILEWRITER_COMMAND_TOPIC = 'AMOR_filewriterConfig'
FILEWRITER_STATUS_TOPIC = 'AMOR_filewriterStatus'

FORWARDER_COMMAND_TOPIC = 'AMOR_forwarderConfig'
FORWARDER_STATUS_TOPIC = 'AMOR_forwarderStatus'
FORWARDER_DATA_TOPIC = 'AMOR_forwarderData'

HISTOGRAM_MEMORY_URL = 'http://amorhm:80/admin'
HISTOGRAM_MEMORY_ENDIANESS = 'big'

DETECTOR_EVENTS_TOPIC = 'amor_ev44'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/amor/'
