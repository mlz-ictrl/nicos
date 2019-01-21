description = 'real flight path'

group = 'lowlevel'

includes = ['det_pos']

devices = dict(
    real_flight_path = device('nicos_mlz.refsans.devices.resolution.RealFlightPath',
        description = description,
        lowlevel = False,
        table = 'det_table',
        pivot = 'det_pivot',
    ),
)
