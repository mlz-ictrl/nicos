description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
    '4.66A': {
        '1.5m':    dict(z=1.5,  x=17.0,  y=602.9),
        '4m':      dict(z=4,    x=16.0,  y=605.0),
        '4m DB':   dict(z=4,    x=16.0,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=18.0,  y=603.0),
        '20m':     dict(z=19.9, x=16.5,  y=598.2),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '5A': {
        '1.5m':    dict(z=1.5,  x=17.0,  y=602.9),
        '2m':      dict(z=2,    x=16.7,  y=603.9),
        '4m':      dict(z=4,    x=16.0,  y=605.0),
        '6m':      dict(z=6,    x=16.0,  y=603.6),
        '8m':      dict(z=8,    x=18.0,  y=603.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=16.5,  y=598.2),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '6A': {
        '2m':      dict(z=2,    x=13.0,  y=610.0),
        '4m DB':   dict(z=4,    x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '7A': {
        '2m':      dict(z=2,    x=13.0,  y=610.0),
        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
        '4m':      dict(z=4,    x=13.0,  y=607.0),
        '8m':      dict(z=8,    x=17.7,  y=602.0),
        '8m DB':   dict(z=8,    x=17.7,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=14.0,  y=592.8),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '8A': {
        '2m':      dict(z=2,    x=13.0,  y=610.0),
        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=2.5,   y=610.0),
        '20m':     dict(z=19.9, x=1.0,   y=610.0),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '9A': {
        '2m':      dict(z=2,    x=13.0,  y=610.0),
        '2m DB':   dict(z=2  ,  x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '10A': {
        '2m':      dict(z=2,    x=16.3,  y=604.0),
        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=16.3,  y=600.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=16.5,  y=579.5),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '19A': {
        '20m':     dict(z=19.9, x=16.0,  y=517.0),
        '20m DB':  dict(z=19.9, x=13.0,  y=603.0, attenuator='in'),
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
