description = 'Generic configuration settings for NEUTRA'

import os

group = 'configdata'

DATA_PATH = os.environ.get('NICOSDUMP', '.') + '/neutra/'

KAFKA_BROKERS = ['localhost:9092']

"""
Below is the full list of all dynamic motors that one day should exist at Neutra
dynamic_motor_suffixes = ['bb_tx',
                          'ne1_tx',
                          'ne2_tx',
                          'ne40_ty',
                          'ne90_ty',
                          'nect_rx',
                          'nect_ry',
                          'nect2_rx',
                          'nect2_ry',
                          'focus_midi',
                          'focus_micro',
                          'nedg_rz',
                          'nedg_rx',
                          'g0_lin',
                          'g0_rot',
                          'g1_rot',
                          'g1_lin',
                          'g2_rot',
                          'samtry',
                          'samtrx',
                          'samtrz',
                          'samrot']
"""

# Currently existing dynamic motors at Neutra
dynamic_motor_suffixes = ['bb_tx',
                          'ne1_tx',
                          'nect_rx',
                          'nect_ry',
                          'focus_midi']
