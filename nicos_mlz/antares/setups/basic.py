description = 'Fundamental Functions of ANTARES'

group = 'lowlevel'

# Here we intend to put fundamental devices always needed for ANTARES
# These will be Shutters, Collimators, Pilz State inputs, ...

includes = [
    'reactor', 'shutters', 'collimator', 'pilz_states', 'center3', #'ubahn',
    'light', 'memograph', 'estops', 'detector_parameters'
]

devices = dict()

monitor_blocks = dict(
    shutters = Block('Shutters & Collimators',
        [
            BlockRow(
                Field(name='Reactor', dev='ReactorPower', width=7),
                Field(dev='collimator', width=10),
                Field(dev='pinhole', width=10),
            ),
            BlockRow(
                Field(dev='shutter1', width=10, istext = True),
                Field(dev='shutter2', width=10, istext = True),
                Field(dev='fastshutter', width=10, istext = True),
            ),
        ],
        setups=setupname,
    ),
    basic = Block('Info',
        [
            BlockRow(
                Field(name='Ambient', dev='Ambient_pressure'),
                Field(name='Flight Tube', dev='Flighttube_pressure'),
                Field(dev='UBahn', width=12, istext=True),
            ),
            BlockRow(
                Field(plot='Pressure', name='Ambient', dev='Ambient_pressure', width=40, height=20, plotwindow=24*3600),
                Field(plot='Pressure', name='Flight Tube', dev='Flighttube_pressure'),
            ),
        ],
        setups=setupname,
    ),
)
