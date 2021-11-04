description = 'Generic configuration settings for ZEBRA'
import os

group = 'configdata'

ZEBRAHM_URL = os.environ.get('ZEBRAHM', 'http://localhost:8080/admin')

HISTOGRAM_MEMORY_ENDIANESS = 'big'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/zebra/'
