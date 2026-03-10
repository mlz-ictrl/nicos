description = 'spin flipper 1 setup'

group = 'lowlevel'

servername = 'EXV6'
nameservice = '172.16.1.1'

devices = dict(
    flip1=device('nicos.devices.vendor.caress.base.Driveable',
                 unit='A',
                 abslimits=(0, 1.5),
                 nameserver='%s' % nameservice,
                 objname='%s' % servername,
                 config='FLIP1_F   105   2    2      10        30.0 	0	1.5',
                 visibility=(),
                 ),
    comp1=device('nicos.devices.vendor.caress.base.Driveable',
                 unit='A',
                 abslimits=(0, 4),
                 nameserver='%s' % nameservice,
                 objname='%s' % servername,
                 config='COMP1_F   105   2    2       9        30.0 	0 	4',
                 visibility=(),
                 ),
    mezeiflipper1=device('nicos.devices.polarized.MezeiFlipper',
                         description='Mezei flipper 1',
                         flip='flip1',
                         corr='comp1',
                         currents=(0.95, 3.12),
                         ),
)
