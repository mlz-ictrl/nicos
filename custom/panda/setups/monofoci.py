#  -*- coding: utf-8 -*-

description = 'Setup of a Monochromator Focusing Box on PANDA'

group = 'lowlevel'

extended = dict(dynamic_loaded = True)

devices = dict(
    # Nicos based access to phytron in magnet rack
    focimotorbus = device('panda.mcc2.TangoSerial',
                          tangodevice = 'tango://phys.panda.frm2:10000/panda/mcc/focibox',
                          lowlevel = True,
                         ),
    focibox = device('panda.mcc2.MCC2Monoframe',
                     bus = 'focimotorbus',
                     description = 'reads monocodes and returns which mono is connected',
                     addr = 0,
                     unit = '',
                    ),

    mfh = device('devices.generic.DeviceAlias',
                 alias = '',
                ),
    mfv = device('devices.generic.DeviceAlias',
                 alias = '',
                ),
)
