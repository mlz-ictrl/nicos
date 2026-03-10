description = 'spin flipper 2 setup'

group = 'lowlevel'

servername = 'EXV6'
nameservice = '172.16.1.1'

devices = dict(
    flip2=device('nicos.devices.vendor.caress.base.Driveable',
                 unit='A',
                 abslimits=(0, 1.5),
                 nameserver='%s' % nameservice,
                 objname='%s' % servername,
                 config='FLIP2_F   105   2    2      15        30.0 	0	1.5',
                 visibility=(),
                 ),
    comp2=device('nicos.devices.vendor.caress.base.Driveable',
                 unit='A',
                 abslimits=(0, 4),
                 nameserver='%s' % nameservice,
                 objname='%s' % servername,
                 config='COMP2_F   105   2    2      14        30.0 	0 	4',
                 visibility=(),
                 ),
    mezeiflipper2=device('nicos.devices.polarized.MezeiFlipper',
                         description='Mezei flipper 2',
                         flip='flip2',
                         corr='comp2',
                         currents=(0.95, 3.12),
                         ),
)
