description = 'resolution args of chopper real table'

group = 'lowlevel'

includes = ['chopper', 'detector', 'real_flight_path']

devices = dict(
    resolution = device('nicos_mlz.refsans.devices.resolution.Resolution',
        description = description,
        lowlevel = False,
        chopper2 = 'chopper2',
        flightpath = 'real_flight_path',
    ),
)
