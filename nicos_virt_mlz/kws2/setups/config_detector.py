description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
    '2.9A tilt': {
        '1.5m':    dict(z=1.5,  x=1.0,  y=520.0),
        '1.5m DB': dict(z=1.5,  x=2.0,  y=500.0),
        '2m':      dict(z=2,    x=1.0,  y=521.5),
        '4m':      dict(z=4,    x=3.0,  y=521.5),
        '8m':      dict(z=8,    x=2.5,  y=520.5),
    },
    '4.66A': {
        '1.5m':    dict(z=1.5,  x=1.0,  y=520),
        '1.5m DB': dict(z=1.5,  x=2.0,  y=500.0),
        '2m':      dict(z=2,    x=1.0,  y=521.5),
        '4m':      dict(z=4,    x=3.0,  y=521.5),
        '8m DB':   dict(z=8,    x=3.0,  y=500.0),
        '8m':      dict(z=8,    x=2.5,  y=520.5),
        '14m':     dict(z=14,   x=3.0,  y=517),
        '20m':     dict(z=19.9, x=3.0,  y=513.5),
    },
    '5A': {
        '1.5m':    dict(z=1.5,  x=1.0,  y=520),
        '1.5m DB': dict(z=1.5,  x=2.0,  y=620.0),
        '2m':      dict(z=2,    x=1.0,  y=521.5),
        '4m':      dict(z=4,    x=3.0,  y=521.5),
        '6m':      dict(z=6,    x=16.0, y=603.6),
        '8m':      dict(z=8,    x=1.5,  y=520.5),
        '8m DB':   dict(z=8,    x=2.0,  y=620.0),
        '20m':     dict(z=19.9, x=3.0,  y=512),
        '20m DB':  dict(z=19.9, x=2.0,  y=620.0),
    },
    '5A tilt': {
        '1.5m':    dict(z=1.5,  x=19.0,  y=596.5),
        '2m':      dict(z=2,    x=15.6,  y=617.0),
        '2m DB':   dict(z=2,    x=13.0,  y=500.0),
        '4m':      dict(z=4,    x=13.7,  y=617.0),
        '6m':      dict(z=6,    x=16.0,  y=603.6),
        '8m':      dict(z=8,    x=16.0,  y=617.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0),
        '8m att':  dict(z=8,    x=13.0,  y=500.0),
        '20m':     dict(z=19.9, x=14.6,  y=592.4),
    },
    '7A': {
        '1.5m':    dict(z=1.5,  x=1.0,   y=520.5),
        '1.5m DB': dict(z=1.5,  x=1.0,   y=500.0),
        '2m':      dict(z=2,    x=1.0,   y=521.5),
        '4m':      dict(z=4,    x=2.5,   y=521.0),
        '8m':      dict(z=8,    x=1.5,   y=520.5),
        '8m DB':   dict(z=8,    x=1.5,   y=300.0),
        '20m DB':  dict(z=19.9, x=1.0,   y=300.0),
        '20m':     dict(z=19.9, x=1.0,   y=507.5),
    },
    '7A tilt': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0),
        '2m':      dict(z=2,    x=18.8,  y=597.9),
        '2m DB':   dict(z=2,    x=16.9,  y=500.0),
        '4m':      dict(z=4,    x=20.3,  y=597.5),
        '8m':      dict(z=8,    x=20.9,  y=592.5),
        '8m DB':   dict(z=8,    x=20.9,  y=500.0),
        '20m':     dict(z=19.9, x=15.0,  y=581.2),
    },
    '10A': {
        '1.5m':    dict(z=1.5,  x=1.0,   y=521.0),
        '1.5m DB': dict(z=1.5,  x=1.0,   y=521.0),
        '2m':      dict(z=2,    x=1.0,   y=521.5),
        '4m':      dict(z=4,    x=1.5,   y=519.0),
        '8m':      dict(z=8,    x=3.0,   y=516.0),
        '8m DB':   dict(z=8,    x=4.0,   y=620.0),
        '20m':     dict(z=19.9, x=4.0,   y=493.5),
        '20m DB':  dict(z=19.9, x=4.0,   y=300.0),
    },
    '19A': {
        '2m':      dict(z=2,    x=1.0,  y=597.8),
        '20m':     dict(z=19.9, x=1.0,  y=620.0),
        '8m':      dict(z=8,    x=1.0,  y=500.0),
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
    14:   0.7,
    17.0: 0.7,     # for small detector
    19.9: 0.7,
}
