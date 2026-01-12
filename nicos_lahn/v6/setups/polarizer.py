description = 'Polarizer setup'

group = 'lowlevel'

devices = dict(

    trans_po=device('nicos.devices.generic.manual.ManualMove',
                    description='vertical movement',
                    abslimits=(0, 600),
                    unit='mm',
                    ),
    rot_po=device('nicos.devices.generic.manual.ManualMove',
                  description='rotation',
                  abslimits=(-40, 40),
                  unit='grades',
                  ),
)
