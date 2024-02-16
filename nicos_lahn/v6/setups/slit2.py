description = 'slit 2 setup'

group = 'lowlevel'

nameservice = '172.16.1.1'
servername_ST169 = 'NVMEV6'
servername_ST222 = 'EXV6'

#corbadevice.dat
loadblock_LE2= '''motion_usefloat=yes
motion_mot_digital input scaling=1092298512
motion_displayformat=%0.2f
motion_display=13
loadoffset=yes
'''

loadblock_RI2='''motion_usefloat=yes
motion_mot_digital input scaling=1092298512
motion_displayformat=%0.2f
motion_display=14
loadoffset=yes
'''

devices = dict(
    up2 = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'beam limiter top blade',
                 visibility = (),
                 abslimits = (-145, 145),
                 nameserver = '%s' % nameservice,
                 objname = '%s' % servername_ST169,
                 config = 'UP2_DI 114 11 0x00f1c000 3 8192 2048 256 2 24 100 '
                         '-1 0 1 5000 10 -50 0 0 0',
    ),
   do2 = device('nicos.devices.vendor.caress.EKFMotor',
                   description='beam limiter bottom blade',
                   visibility = (),
                   abslimits = (-145, 145),
                   ameserver = '%s' % nameservice,
                   objname = '%s' % servername_ST169,
                   config = 'DO2_DI 114 11 0x00f1c000 4 8192 2048 256 2 24 '
                           '100 -1 0 1 5000 10 -50 0 0 0',
   ),
   le2 = device('nicos.devices.vendor.caress.Motor',
                 description='beam limiter left blade',
                 visibility = (),
                 abslimits = (-35, 45),
                 nameserver = '%s' % nameservice,
                 objname = '%s' % servername_ST222,
                 config = 'LE2_DI 500 172.16.1.3:/st222.caress_object '
                         'CopleyStepnet 5 4000 BeckhoffKL5001 BK5120 63/32/16/0 4096 8081353',
                 loadblock = loadblock_LE2,
   ),
   ri2 = device('nicos.devices.vendor.caress.Motor',
                  description='beam limiter right blade',
                  visibility = (),
                  abslimits = (-35, 45),
                  nameserver = '%s' % nameservice,
                  objname = '%s' % servername_ST222,
                  config = 'RI2_DI 500 172.16.1.3:/st222.caress_object '
                          'CopleyStepnet 6 4000 BeckhoffKL5001 BK5120/63/32/20/0 4096 7914523',
                  loadblock = loadblock_RI2,
    ),
    slit_2 = device('nicos.devices.generic.slit.Slit',
                    description = 'slit 2',
                    left='le2',
                    right='ri2',
                    top='up2',
                    bottom='do2',
                    opmode='offcentered',
                    coordinates='opposite',
                    fmtstr='%.2f',
                    unit='mm',
    ),
)
