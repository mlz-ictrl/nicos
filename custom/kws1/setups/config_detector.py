description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the z position and x/y displacement of the detector for
# each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
    '5A': {
        '1.5m':    dict(z=1.5, x=-5.0,  y=9.7),
        '2m':      dict(z=2,   x=-4.5,  y=9.1),
        '4m':      dict(z=4,   x=-3.2,  y=8.0),
        '8m':      dict(z=8,   x=-3.0,  y=7.0),
        '14m':     dict(z=14,  x=-3.0,  y=5.2),
        '20m':     dict(z=20,  x=-4.5,  y=1.0),
        '6m Hum':  dict(z=6,   x=-3.5,  y=8.0),
        '1.5m Tr': dict(z=1.5, x=-25,   y=-40),
        '2m Tr':   dict(z=2,   x=-25,   y=-40),
        '8m Tr':   dict(z=8,   x=-25,   y=-40),
        '20m Tr':  dict(z=20,  x=-25,   y=-40),
    },
    '6A': {
        '1.5m':    dict(z=1.5, x=-5.0,  y=9.7),
        '2m':      dict(z=2,   x=-5.0,  y=9.3),
        '4m':      dict(z=4,   x=-3.5,  y=7.8),
        '8m':      dict(z=8,   x=-3.0,  y=6.7),
        '20m':     dict(z=20,  x=-4.0,  y=-3.0),
        '8m Tr':   dict(z=8,   x=-25,   y=-40),
    },
    '7A': {
        '1.5m':    dict(z=1.5, x=-3.5,  y=9.0),
        '2m':      dict(z=2,   x=-3.5,  y=9.0),
        '4m':      dict(z=4,   x=-2.0,  y=7.3),
        '8m':      dict(z=8,   x=-1.5,  y=6.5),
        '14m':     dict(z=14,  x=-3.3,  y=2.0),
        '20m':     dict(z=20,  x=-2.9,  y=-4.5),
        '8m Tr':   dict(z=8,   x=-25,   y=-40),
        '18.3m C20 Lens': dict(z=18.3, x=-3, y=-7),
    },
    '8A': {
        '8m Tr':   dict(z=8,   x=-25,   y=-40),
    },
    '10A': {
        '1.5m':    dict(z=1.5, x=-4.1,  y=8.1),
        '2m':      dict(z=2,   x=-4.1,  y=8.1),
        '4m':      dict(z=4,   x=-2.7,  y=6.7),
        '8m':      dict(z=8,   x=-1.9,  y=4.5),
        '14m':     dict(z=14,  x=-3.0,  y=-4.0),
        '20m':     dict(z=20,  x=-1.8,  y=-21.5),
        '8m Tr':   dict(z=8,   x=-25,   y=-40),
        '6.4m C20 Lens':  dict(z=6.4,  x=-2.5, y=1.0),
        '10.4m C14 Lens': dict(z=10.4, x=-2.2, y=2.0),
    },
    '12A': {
        '1.5m':    dict(z=1.5, x=-4.0,  y=8.0),
        '2m':      dict(z=2,   x=-4.0,  y=8.0),
        '4m':      dict(z=4,   x=-1.5,  y=6.5),
        '8m':      dict(z=8,   x=-2.7,  y=1.3),
        '20m':     dict(z=20,  x=-3.2,  y=-29.7),
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
}
