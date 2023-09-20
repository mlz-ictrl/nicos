description = 'Generic configuration settings for SANS-LLB'
import os

group = 'configdata'

JUST_BIN_IT_COMMANDS_TOPIC = 'SANSLLB_histCommands'
JUST_BIN_IT_RESPONSES_TOPIC = 'SANSLLB_histResponse'
JUST_BIN_IT_HISTOGRAMS_TOPIC = 'SANSLLB_histograms'
JUST_BIN_IT_DATA_TOPIC = 'SANSLLB_detector'

KAFKA_BROKERS = [os.environ.get('KAFKABROKERS', 'linkafka01.psi.ch:9092')]


DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/sans-llb/'
