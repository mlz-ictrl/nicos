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
        '2m':      dict(z=2,    x=19.0,  y=609.3),
        '4m':      dict(z=4,    x=19.5,  y=610.7),
        '8m DB':   dict(z=8,    x=21.3,  y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=21.3,  y=612.6),
        '20m':     dict(z=19.9, x=20.7,  y=605.7),
        'Small':   dict(det='small', x=0.0, y=711.4),
##########################################################################
############################# ACHTUNG ####################################
# New beamstop values measured on 16.03.2017 for 2, 4, 8, and 20m at 5 A
# wavelength
##########################################################################
##########################################################################
    },
    '5A': {
#       '1.5m':    dict(z=1.5,  x=17.0,  y=602.9),
        '2m':      dict(z=2,    x=17.5,  y=612.0),
        '4m':      dict(z=4,    x=18.8,  y=613.5),
#       '6m':      dict(z=6,    x=16.0,  y=603.6),
        '8m':      dict(z=8,    x=19.8,  y=615.5),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=18.8,  y=609.8),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '6A': {
        '2m':      dict(z=2,    x=13.0,  y=610.0),
        '4m DB':   dict(z=4,    x=13.0,  y=500.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
    '7A': {
        '2m':      dict(z=2,    x=16.9,  y=606.6),
        '2m DB':   dict(z=2,    x=16.9,  y=500.0, attenuator='in'),
        '4m':      dict(z=4,    x=18.0,  y=606.8),
        '8m':      dict(z=8,    x=20.0,  y=607.1),
        '8m DB':   dict(z=8,    x=20.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=16.5,  y=592.8),
        'Small':   dict(det='small', x=13.8, y=711.4),
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
#only 20 m have been updated at lambda = 10 A
    },
    '10A': {
        '2m':      dict(z=2,    x=16.3,  y=604.0),
        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
        '4m':      dict(z=4,    x=16.3,  y=604.0),
        '8m':      dict(z=8,    x=16.3,  y=600.0),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=20.1,  y=589.0),
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
