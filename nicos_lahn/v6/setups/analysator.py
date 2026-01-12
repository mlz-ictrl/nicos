description = 'Analysator setup'

group = 'lowlevel'
excludes = ['offspecularanalysator', 'spinflipper2']

devices = dict(
    trans_an=device('nicos.devices.generic.manual.ManualMove',
                    description='vertical movement',
                    abslimits=(0, 600),
                    unit='mm',
                    ),
    rot_an=device('nicos.devices.generic.manual.ManualMove',
                  description='rotation',
                  abslimits=(-40, 40),
                  unit='grades',
                  ),
)
