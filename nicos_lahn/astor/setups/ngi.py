description = 'neutron grating interferometer #0 setup'

group = 'optional'

excludes = ['monochromator']

devices = dict(
    tx=device('nicos.devices.generic.VirtualMotor',
              description='translation x',
              abslimits=(-25, 25),
              unit='mm',
              fmtstr='%d',
              precision=0.1,
              requires={'level': 'admin'},
              speed=1,
              ),
    ry=device('nicos.devices.generic.VirtualMotor',
              description='rotation y',
              abslimits=(0, 10),
              unit='deg',
              fmtstr='%d',
              precision=1,
              requires={'level': 'admin'},
              speed=1,
              ),
    rz=device('nicos.devices.generic.VirtualMotor',
              description='rotation z',
              abslimits=(0, 90),
              unit='deg',
              fmtstr='%d',
              precision=1,
              requires={'level': 'admin'},
              speed=1,
              ),
)
