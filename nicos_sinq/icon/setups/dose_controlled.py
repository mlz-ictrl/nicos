description = 'Setup for dose controlled motorization'

pvprefix = 'SQ:ICON:sumi:'
pvprefix_ai = 'SQ:ICON:B5ADC:'

includes = ['shutters']
excludes = ['detector', 'detector_phys']

display_order = 90

devices = dict(
    beam_current = device('nicos.devices.epics.EpicsReadable',
        description = 'Beam current',
        readpv = pvprefix_ai + 'V4',
        epicstimeout = 3.0
    ),
    dose_value = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = 3.0,
        description = 'Interal dose value in uA*s',
        readpv = pvprefix + 'BEAMINT',
    ),
    dose_switch = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = 3.0,
        description = 'Switch for dose integration',
        readpv = pvprefix + 'SWITCH',
        writepv = pvprefix + 'SWITCH',
    ),
    dose_reset = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Reset of integral does (set to 0 for resetting)',
        readpv = pvprefix + 'ACCINT',
        writepv = pvprefix + 'ACCINT',
        abslimits = (0, 1e10),
        epicstimeout = 3.0
    ),
    phys_trig = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = 3.0,
        description = 'Switch for dose integration',
        readpv = pvprefix + 'PHYS',
        writepv = pvprefix + 'PHYS',
    ),
)
