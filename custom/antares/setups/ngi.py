description = 'Neutron Grating Interferometer'

group = 'optional'

excludes = ['ngi_jcns']

devices = dict(
    G0rz = device('devices.taco.Motor',
                        speed = 2,
                        unit = 'deg',
                        description = 'Rotation of G0 grating around beam direction',
                        tacodevice = 'antares/copley/m01',
                        abslimits = (-400, 400),
                        userlimits = (-400, 400),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    G0ry = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'deg',
                        description = 'Rotation of G0 grating around vertical axis',
                        tacodevice = 'antares/copley/m02',
                        abslimits = (-1, 400),
                        userlimits = (-1, 400),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    G0tx = device('devices.taco.Motor',
                        speed = 1,
                        unit = 'mm',
                        description = 'Stepping of G0 perpendicular to the beam direction',
                        tacodevice = 'antares/copley/m03',
                        abslimits = (-9, 400),
                        userlimits = (-9, 400),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    G1rz = device('devices.taco.Motor',
                        speed = 0.3,
                        unit = 'deg',
                        description = 'Rotation of G1 grating around beam direction',
                        tacodevice = 'antares/copley/m04',
                        abslimits = (-400, 400),
                        userlimits = (-400, 400),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    G1tz = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'mm',
                        description = 'Translation of G1 in beam direction. (Talbot distance)',
                        tacodevice = 'antares/copley/m05',
                        abslimits = (-99999, 99999),
                        userlimits = (-99999, 99999),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    G12rz = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'deg',
                        description = 'Rotation of G2 and G1 around beam axis',
                        tacodevice = 'antares/copley/m07',
                        abslimits = (-400, 400),
                        userlimits = (-250, 250),
                        maxage = 5,
                        pollinterval = 3,
                      ),

)
