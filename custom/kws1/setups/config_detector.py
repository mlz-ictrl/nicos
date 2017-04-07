description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the z position and x/y displacement of the detector for
# each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
    '5A': {
        '1.5m':    dict(z=1.5, x=-3.0,  y=7.9),
        '2m':      dict(z=2,   x=-3.0,  y=7.9),
        '4m':      dict(z=4,   x=-0.0,  y=8.5),
        '8m':      dict(z=8,   x=-1.1,  y=6.1),
        '14m':     dict(z=14,  x=-2.8,  y=4.4),
        '20m':     dict(z=20,  x=-2.6,  y=-0.4),
        '6m Hum':  dict(z=6,   x=-1.0,  y=7.0),
        '1.5m Tr': dict(z=1.5, x=-25,   y=-50),
        '2m Tr':   dict(z=2,   x=-25,   y=-50),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '6A': {
        '1.5m':    dict(z=1.5, x=-3.5,  y=8.0),
        '2m':      dict(z=2,   x=-3.5,  y=8.0),
        '4m':      dict(z=4,   x=-2.0,  y=6.5),
        '8m':      dict(z=8,   x=-1.2,  y=5.5),
        '14m':     dict(z=14,  x=-2.5,  y=2.7),
        '20m':     dict(z=20,  x=-2.0,  y=-3.0),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '7A': {
        '1.5m':    dict(z=1.5, x=-2.8,  y=8.3),
        '2m':      dict(z=2,   x=-2.8,  y=8.3),
        '4m':      dict(z=4,   x=-1.8,  y=6.8),
        '8m':      dict(z=8,   x=-1.0,  y=5.3),
        '14m':     dict(z=14,  x=-2.8,  y=1.1),
        '20m':     dict(z=20,  x=-2.2,  y=-5.8),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '18.3m C20 Lens': dict(z=18.3, x=-3, y=-7),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '8A': {
        '1.5m':    dict(z=1.5, x=-3.7,  y=8.7),
        '2m':      dict(z=2,   x=-3.7,  y=8.7),
        '4m':      dict(z=4,   x=-2.5,  y=6.7),
        '8m':      dict(z=8,   x=-1.5,  y=5.3),
        '14m':     dict(z=14,  x=-2.5,  y=-0.5),
        '20m':     dict(z=20,  x=-2.5,  y=-8.5),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '9A': {
        '1.5m':    dict(z=1.5, x=-3.2,  y=8.5),
        '4m':      dict(z=4,   x=-2.2,  y=6.5),
        '20m':     dict(z=20,  x=-1.8,  y=-13),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '10A': {
        '1.5m':    dict(z=1.5, x=-2.7,  y=8.2),
        '2m':      dict(z=2,   x=-2.7,  y=8.2),
        '4m':      dict(z=4,   x=-2.0,  y=6.2),
        '8m':      dict(z=8,   x=-0.9,  y=3.8),
        '14m':     dict(z=14,  x=-2.6,  y=-4.9),
        '20m':     dict(z=20,  x=-1.0,  y=-18.0),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '12m':     dict(z=12,  x=-3.0,  y=-2.0),
        '6.4m C20 Lens':  dict(z=6.4,  x=-2.5, y=1.0),
        '10.4m C14 Lens': dict(z=10.4, x=-2.2, y=2.0),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '11A': {
        '1.5m':    dict(z=1.5, x=-2.7,  y=8.2),
        '4m':      dict(z=4,   x=-1.7,  y=6.0),
        '20m':     dict(z=20,  x=-3.5,  y=-24.2),
        '4m Tr':   dict(z=4,   x=-25,   y=-50),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '12A': {
        '1.5m':    dict(z=1.5, x=-2.8,  y=8.2),
        '2m':      dict(z=2,   x=-2.8,  y=8.2),
        '4m':      dict(z=4,   x=-1.5,  y=5.7),
        '8m':      dict(z=8,   x=-0.7,  y=2.2),
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '14m':     dict(z=14,  x=-1.9,  y=-9.0),
        '20m':     dict(z=20,  x=-6.0,  y=-30.5),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
    '20A': {
        '8m Tr':   dict(z=8,   x=-25,   y=-50),
        '20m':     dict(z=20,  x=-25,   y=1.0),
        '20m Tr':  dict(z=20,  x=-25,   y=-50),
    },
}

# This offset is added to 20m + det_z to get the chopper-detector length
# for time-of-flight mode calculation.
#
# It varies with detector distance because the det_z value is not actually
# particularly accurate.

DETECTOR_OFFSETS = {
    2:    2.21,
    4:    2.218,
    8:    2.23,
    14:   2.248,
    18.3: 2.26,
    20:   2.266,
    1.5:  2.21,
    # Taken from a linear interpolation of the above measured values.
    6:    2.223,
    6.4:  2.225,
    10.4: 2.237,
    12:   2.24,
}
