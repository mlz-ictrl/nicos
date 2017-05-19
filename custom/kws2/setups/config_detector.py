description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
    '3A': {
        '2m':      dict(z=2,    x=13.0,  y=596.8),
        '8m':      dict(z=8,    x=22.5,  y=593.8),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
        '20m DB':  dict(z=19.9, x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=21.0,  y=586.0),
    },
    '4.66A': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
        '2m':      dict(z=2,    x=18.8,  y=597.8),
        '4m':      dict(z=4,    x=20.3,  y=597.5),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=22.5,  y=593),
        '20m':     dict(z=19.9, x=21.0,  y=586.0),
        'Small':   dict(det='small', x=0.0, y=711.4),
##########################################################################
############################# ACHTUNG ####################################
# New beamstop values measured on 03.05.2017 for 2, 4, 8, and 20m at 5 A
# wavelength
##########################################################################
##########################################################################
    },
    '5A': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
        '2m':      dict(z=2,    x=18.8,  y=597.8),
        '4m':      dict(z=4,    x=20.3,  y=597.5),
#       '6m':      dict(z=6,    x=16.0,  y=603.6),
        '8m':      dict(z=8,    x=21.5,  y=593.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '8m att':  dict(z=8,    x=13.0,  y=500.0),
        '20m':     dict(z=19.9, x=18.0,  y=590.0),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '6A': {
        '2m':      dict(z=2,    x=13.0,  y=597.8),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '7A': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
        '2m':      dict(z=2,    x=18.8,  y=597.9),
        '2m DB':   dict(z=2,    x=16.9,  y=500.0, attenuator='in'),
        '4m':      dict(z=4,    x=20.3,  y=597.5),
        '8m':      dict(z=8,    x=22.0,  y=592.0),
        '8m DB':   dict(z=8,    x=20.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=20.5,  y=581.2),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '8A': {
        '2m':      dict(z=2,    x=13.0,  y=597.8),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=2.5,   y=610.0),
        '20m':     dict(z=19.9, x=1.0,   y=610.0),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '9A': {
        '2m':      dict(z=2,    x=13.0,  y=597.8),
        '8m DB':   dict(z=8  ,  x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
#only 20 m have been updated at lambda = 10 A
    },
    '10A': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
        '2m':      dict(z=2,    x=18.8,  y=597.8),
        '4m':      dict(z=4,    x=16.3,  y=604.0),
        '8m':      dict(z=8,    x=16.3,  y=600.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=21.5,  y=567.8),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '11.3A': {
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '4m':      dict(z=4,    x=16.3,  y=604.0),
#        '8m':      dict(z=8,    x=16.3,  y=600.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '20m':     dict(z=19.9, x=21.5,  y=567.2),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '19A': {
        '20m':     dict(z=19.9, x=16.0,  y=517.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
}

SMALL_DET_POSITION = 17.0

# This offset is added to 20m + det_z to get the chopper-detector length
# for time-of-flight mode calculation.
#
# It varies with detector distance because the det_z value is not actually
# particularly accurate.

DETECTOR_OFFSETS = {
    1.5:  0.7,
    2:    0.7,
    2.1:  0.7,
    4:    0.7,
    4.1:  0.7,
    6:    0.7,
    8:    0.7,
    8.1:  0.7,
    17.0: 0.7,     # for small detector
    19.9: 0.7,
}
