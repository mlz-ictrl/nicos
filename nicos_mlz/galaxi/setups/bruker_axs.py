# -*- coding: utf-8 -*-

description = 'Bruker AXS liquid metal jet x-ray source at GALAXI'

group = 'basic'

display_order = 5

tango_base = 'tango://phys.galaxi.kfa-juelich.de:10000/galaxi/'
metaljet = tango_base + 'metaljet/'

devices = dict(
    generator_voltage = device('nicos.devices.tango.AnalogInput',
        description = 'Applied voltage to the generator of the x-ray source',
        tangodevice = metaljet + 'comp_generator_voltage',
        unit = 'kV',
    ),
    generator_current = device('nicos.devices.tango.AnalogInput',
        description = 'Applied current to the generator of the x-ray source',
        tangodevice = metaljet + 'comp_generator_current',
        unit = 'mA',
    ),
    spot_position_x = device('nicos.devices.tango.AnalogInput',
        description = 'Metal jet spot position in x direction',
        tangodevice = metaljet + 'comp_spot_position_x',
    ),
    time_since_calib = device('nicos.devices.tango.AnalogInput',
        description = 'Elapsed time since last calibration',
        tangodevice = metaljet + 'comp_time_since_calibration',
    ),
    calib_interval = device('nicos.devices.tango.AnalogInput',
        description = 'Maximum interval between two calibrations',
        tangodevice = metaljet + 'comp_calibration_interval',
        fmtstr = '%d',
    ),
    uptime = device('nicos.devices.tango.AnalogInput',
        description = 'Operation hours since last restart',
        tangodevice = metaljet + 'comp_operation_hours',
    ),
    stigmator_current = device('nicos.devices.tango.AnalogInput',
        description = 'Applied current to the metal jet stigmator',
        tangodevice = metaljet + 'comp_stigmator_current',
    ),
    vacuum_pressure = device('nicos.devices.tango.AnalogInput',
        description = 'Current metal jet vacuum pressure',
        tangodevice = metaljet + 'comp_vacuum_pressure',
        fmtstr = '%.4g',
    ),
    shutter = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Shutter device of the x-ray source',
        tangodevice = metaljet + 'comp_shutter',
        mapping = {
            'closed': 0,
            'open': 1,
        },
    ),
    tubecond = device('nicos_mlz.galaxi.devices.bruker_axs.TubeConditioner',
        description = 'Tube conditioning device of the x-ray source',
        tangodevice = metaljet + 'comp_tube_conditioner',
        mapping = {
           'unknown': 0,
           'running': 1,
           'green': 2,
           'yellow': 3,
           'red': 4,
           'violet': 5,
        },
        unit = '',
    ),
)
