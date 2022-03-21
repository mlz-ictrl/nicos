name = 'SINQ BOA Counter Rotation'

includes = ['stdsystem']

devices = dict(
    rb=device('nicos.devices.generic.VirtualMotor',
              unit='mm',
              abslimits=(-100, 100), ),
    rc=device('nicos.devices.generic.VirtualMotor',
              unit='mm',
              abslimits=(-100, 100), ),
    rbu=device('nicos_sinq.boa.devices.counterrotation.CounterRotatingMotor',
               description='Counter Rotation Tester',
               master='rb',
               slave='rc',
               unit='mm',
               target=0,
    ),
)
