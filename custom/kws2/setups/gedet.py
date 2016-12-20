# Setup for the GE detector
description = 'large GE He-3 detector'
group = 'lowlevel'

import sys
sys.path.insert(0, '/home/kws2/local/gedetector/test/py')
try:
    import common
except ImportError:  # Jenkins/local
    class common(object):
        mnames = dict(("ep%02d" % i, "") for i in range(1, 19))

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict()


for ep in range(1, 19):
    epname = 'ep%02d' % ep
    devices[epname + '_T']  = device('devices.epics.EpicsReadable',
                                     description = epname + ' FPGA temperature',
                                     readpv = common.mnames[epname] + ':FpgaTemperature',
                                     unit = 'degC',
                                     pollinterval = 10,
                                     fmtstr = '%.1f',
                                     warnlimits = (25, 75))
    devices[epname + '_TB'] = device('devices.epics.EpicsReadable',
                                     description = epname + ' board temperature',
                                     readpv = common.mnames[epname] + ':RsppTemperature',
                                     unit = 'degC',
                                     pollinterval = 10,
                                     fmtstr='%.1f',
                                     warnlimits = (25, 45))
    devices[epname + '_HV'] = device('devices.epics.EpicsReadable',
                                     description = epname + ' HV setting',
                                     readpv = common.mnames[epname] + ':HighVoltage_R',
                                     unit = 'V',
                                     pollinterval = 10,
                                     fmtstr = '%.0f',
                                     warnlimits = (1520, 1540))

for ti in range(1, 3):
    devices['ps%d_V' % ti] = device('devices.tango.PowerSupply',
                                    description = 'detector power supply voltage',
                                    tangodevice = tango_base + 'gesupply/ps%d' % ti,
                                    unit = 'V',
                                    abslimits = (0, 54),
                                    userlimits = (0, 54),
                                    warnlimits = (53.9, 54.1))
    devices['ps%d_I' % ti] = device('devices.generic.ReadonlyParamDevice',
                                    description = 'detector power supply current',
                                    device = 'ps%d_V' % ti,
                                    parameter = 'current',
                                    unit = 'A',
                                    warnlimits = (2.8, 3.2))
