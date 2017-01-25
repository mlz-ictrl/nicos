#  -*- coding: utf-8 -*-

description = 'setup for sample attenuator'

group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    sat_in  = device('devices.tango.DigitalInput',
                     tangodevice = tango_base + 'sat/input',
                     lowlevel = True,
                    ),
    sat_out = device('devices.tango.DigitalOutput',
                     tangodevice = tango_base + 'sat/output',
                     lowlevel = True,
                    ),

    sat = device('panda.satbox.SatBox',
                 description = 'Sample beam attenuator',
                 input = 'sat_in',
                 output = 'sat_out',
                 unit = 'mm',
                 fmtstr = '%d',
                 blades = [1, 2, 5, 10, 20],
                 #blades = [0, 2, 5, 10, 20], # code for nonworking blade
                 readout = 'switches',
                ),
)
