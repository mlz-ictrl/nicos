description = 'MCU200 controller with 2 axes.'

devices = dict(
    motor=device('nicos_ess.v20.devices.mcu200.MCU200Motor',
                 description='Linear axis for gratings.',
                 requires={'level': 'user'},
                 fmtstr='%.2f',
                 unit='mu',
                 abslimits=(0, 5000),
                 host='192.168.1.1:4001',
                 index=1,
                 precision=0.5
                 ),
    rot=device('nicos_ess.v20.devices.mcu200.MCU200Motor',
               description='Rotation stage.',
               requires={'level': 'user'},
               fmtstr='%.2f',
               unit='deg/100',
               abslimits=(0, 36000),
               host='192.168.1.1:4001',
               index=2,
               precision=0.5,
               ),
)
