description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

FIXED_X = 0.0
FIXED_Y = 425.0
FIXED_Y_TR = 290.0
FIXED_Y_GISANS = 400.0


DETECTOR_PRESETS = {
    '5A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '14m':     dict(z=14,   x=FIXED_X,  y=FIXED_Y),
        '20m':     dict(z=20,   x=FIXED_X,  y=FIXED_Y),
        '8m Tr':   dict(z=8,    x=FIXED_X,  y=FIXED_Y_TR),
        '4m Tr':   dict(z=4,    x=FIXED_X,  y=FIXED_Y_TR),
        '20m Tr':  dict(z=20,   x=FIXED_X,  y=FIXED_Y_TR),
        '20m GISANS': dict(z=20, x=FIXED_X, y=FIXED_Y_GISANS),
    },
    '6A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
    },
    '7A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '14m':     dict(z=14,   x=FIXED_X,  y=FIXED_Y),
        '20m':     dict(z=20,   x=FIXED_X,  y=FIXED_Y),
        '8m Tr':   dict(z=8,    x=FIXED_X,  y=FIXED_Y_TR),
        '20m Tr':  dict(z=20,   x=FIXED_X,  y=FIXED_Y_TR),
    },
    '8A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
    },
    '10A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
        '4m':      dict(z=4,    x=FIXED_X,  y=FIXED_Y),
        '8m':      dict(z=8,    x=FIXED_X,  y=FIXED_Y),
        '14m':     dict(z=14,   x=FIXED_X,  y=FIXED_Y),
        '20m':     dict(z=20,   x=FIXED_X,  y=FIXED_Y),
        '8m Tr':   dict(z=8,    x=FIXED_X,  y=FIXED_Y_TR),
        '20m Tr':  dict(z=20,   x=FIXED_X,  y=FIXED_Y_TR),
    },
    '11A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
    },
    '12A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
        '8m Tr':   dict(z=8,    x=FIXED_X,  y=FIXED_Y_TR),
        '20m':     dict(z=20,   x=FIXED_X,  y=FIXED_Y),
        '20m Tr':  dict(z=20,   x=FIXED_X,  y=FIXED_Y_TR),
    },
    '20A': {
        '1.5m':    dict(z=1.5,  x=FIXED_X,  y=FIXED_Y),
        '2.3m':    dict(z=2.3,  x=FIXED_X,  y=FIXED_Y),
        '8m Tr':   dict(z=8,    x=FIXED_X,  y=FIXED_Y_TR),
        '20m':     dict(z=20,   x=FIXED_X,  y=FIXED_Y),
        '20m Tr':  dict(z=20,   x=FIXED_X,  y=FIXED_Y_TR),
    },
}

# This offset is added to 20m + det_z to get the chopper-detector length
# for time-of-flight mode calculation.
#
# It varies with detector distance because the det_z value is not actually
# particularly accurate.

DETECTOR_OFFSETS = {
    2:    2.21,
    2.3:  2.21,
    4:    2.21,
    8:    2.21,
    14:   2.21,
    20:   2.21,
    1.5:  2.21,
    1.6:  2.21,
    6:    2.21,
    18.3: 2.21,
    6.4:  2.21,
    10.4: 2.21,
    12:   2.21,
    17.5: 2.21,
    19.9: 2.21,
}
