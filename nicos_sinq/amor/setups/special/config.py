description = 'Generic configuration settings for AMOR'

group = 'configdata'

KAFKA_BROKERS = ['ess01:9092']

FILEWRITER_CMD_TOPIC= 'kafka-to-nexus.commands'
FILEWRITER_STATUS_TOPIC= 'kafka-to-nexus.status'

FORWARDER_CMD_TOPIC= 'forward-epics-to-kafka.commands'
FORWARDER_STATUS_TOPIC= 'forward-epics-to-kafka.status'

HISTOGRAM_MEMORY_URL = 'http://amorhm:80/admin'
HISTOGRAM_MEMORY_ENDIANESS = 'big'
