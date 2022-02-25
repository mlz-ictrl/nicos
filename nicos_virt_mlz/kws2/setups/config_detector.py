description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

FIXED_X = 0.0
FIXED_X_TILT = 16.0
FIXED_Y = 520.0

DETECTOR_PRESETS = {
    '2.9A tilt': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X,  y=500.0),
        '2m':      dict(z=2,    x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
    },
    '4.66A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X,  y=500.0),
        '2m':      dict(z=2,    x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X,  y=500.0),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '14m':     dict(z=14,   x=FIXED_X,  y=FIXED_Y),
        '20m':     dict(z=19.9, x=FIXED_X,  y=FIXED_Y),
    },
    '5A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X,  y=620.0),
        '2m':      dict(z=2,    x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '6m':      dict(z=6,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X,  y=620.0),
        '20m':     dict(z=19.9, x=FIXED_X,  y=FIXED_Y),
        '20m DB':  dict(z=19.9, x=FIXED_X,  y=620.0),
    },
    '5A tilt': {
        '1.5m':    dict(z=1.5,  x=FIXED_X_TILT,  y=FIXED_Y),
        '2m':      dict(z=2,    x=FIXED_X_TILT,  y=FIXED_Y),
        '2m DB':   dict(z=2,    x=FIXED_X_TILT,  y=500.0),
        '4m':      dict(z=4,    x=FIXED_X_TILT,  y=FIXED_Y),
        '6m':      dict(z=6,    x=FIXED_X_TILT,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X_TILT,  y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X_TILT,  y=500.0),
        '20m':     dict(z=19.9, x=FIXED_X_TILT,  y=FIXED_Y),
    },
    '7A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,   y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X,   y=500.0),
        '2m':      dict(z=2,    x=FIXED_X,   y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,   y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,   y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X,   y=300.0),
        '20m DB':  dict(z=19.9, x=FIXED_X,   y=300.0),
        '20m':     dict(z=19.9, x=FIXED_X,   y=FIXED_Y),
    },
    '7A tilt': {
        '1.5m':    dict(z=1.5,  x=FIXED_X_TILT,  y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X_TILT,  y=500.0),
        '2m':      dict(z=2,    x=FIXED_X_TILT,  y=FIXED_Y),
        '2m DB':   dict(z=2,    x=FIXED_X_TILT,  y=500.0),
        '4m':      dict(z=4,    x=FIXED_X_TILT,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X_TILT,  y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X_TILT,  y=500.0),
        '20m':     dict(z=19.9, x=FIXED_X_TILT,  y=FIXED_Y),
    },
    '10A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,   y=FIXED_Y),
        '1.5m DB': dict(z=1.5,  x=FIXED_X,   y=500.0),
        '2m':      dict(z=2,    x=FIXED_X,   y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,   y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,   y=FIXED_Y),
        '8m DB':   dict(z=8,    x=FIXED_X,   y=620.0),
        '20m':     dict(z=19.9, x=FIXED_X,   y=FIXED_Y),
        '20m DB':  dict(z=19.9, x=FIXED_X,   y=300.0),
    },
    '19A': {
        '2m':      dict(z=2,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '20m':     dict(z=19.9, x=FIXED_X,  y=FIXED_Y),
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
