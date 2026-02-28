description = 'Generic configuration settings for AMOR'
import os

group = 'configdata'

KAFKA_BROKERS = [os.environ.get('KAFKABROKERS', 'linkafka01.psi.ch:9092')]
NICOS_FORWARDER_TOPIC = 'amor_nicosForwarder'

FILEWRITER_COMMAND_TOPIC = 'amor_filewriterConfig'
FILEWRITER_STATUS_TOPIC = 'amor_filewriterStatus'
FILEWRITER_POOL_TOPIC = 'amor_filewriterPool'

HIST_COMMANDS_TOPIC = 'amor_histCommands'
DETECTOR_HISTOGRAM_YZ_TOPIC = 'amor_histograms_YZ'
DETECTOR_HISTOGRAM_TOFZ_TOPIC = 'amor_histograms_TofZ'

DETECTOR_EVENTS_TOPIC = 'amor_detector'
DETECTOR_RATE_TOPIC = 'amor_detector_rate'
MONITOR_EVENTS_TOPIC = 'amor_beam_monitor'
CHOPPER_TRIGGER_TOPIC = 'amor_chopper_trigger'

DATA_PATH = os.environ.get('NICOSDUMP', '.')
SCRIPT_ROOT = "/home/sinquser"
