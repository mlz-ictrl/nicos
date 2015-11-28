# Setup for the GE detector
description = 'large GE He-3 detector'
group = 'lowlevel'

import sys
sys.path.insert(0, '/home/kws2/local/gedetector/test/py')
import common

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict()


for ep in range(1, 19):
    epname = 'ep%02d' % ep
    devices[epname + '_T']  = device('devices.epics.EpicsReadable',
                                     readpv = common.mnames[epname] + ':RsppTemperature',
                                     unit = 'degC',
                                     pollinterval = 10,
                                     fmtstr = '%.1f',
                                     warnlimits = (25, 50))
    devices[epname + '_HV'] = device('devices.epics.EpicsReadable',
                                     readpv=common.mnames[epname] + ':HighVoltage_R',
                                     unit = 'V',
                                     pollinterval = 10,
                                     fmtstr = '%.0f',
                                     warnlimits = (1780, 1820))

for ti in range(1, 3):
    devices['ps%d_V' % ti] = device('devices.tango.PowerSupply',
                                    tangodevice = tango_base + 'gesupply/ps%d' % ti,
                                    unit = 'V',
                                    abslimits = (0, 54),
                                    userlimits = (0, 54),
                                    warnlimits = (53.9, 54.1))
    devices['ps%d_I' % ti] = device('devices.generic.ReadonlyParamDevice',
                                    device = 'ps%d_V' % ti,
                                    parameter = 'current',
                                    unit = 'A',
                                    warnlimits = (2.8, 3.2))
