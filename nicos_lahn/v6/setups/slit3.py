description = 'slit 3 setup'

group = 'lowlevel'

nameservice = '172.16.1.1'
servername_ST169 = 'NVMEV6'
servername_ST222 = 'EXV6'

#corbadevice.dat
loadblock_LE3 = '''motion_usefloat=yes
motion_enc_signedbits=24
motion_displayformat=%0.2f
motion_display=15
loadoffset=yes
'''

loadblock_RI3 = '''motion_usefloat=yes
motion_enc_signedbits=24
motion_displayformat=%0.2f
motion_display=16
loadoffset=yes
'''

devices = dict(
    up3 = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'beam limiter top blade',
                 visibility = (),
                 abslimits = (-145, 145),
                 nameserver = '%s' % nameservice,
                 objname = '%s' % servername_ST169,
                 config = 'UP3_DI 114 11 0x00f1d000 3 -10243 2048 256 2 24 '
                         '100 1 0 1 5000 10 50 0 0 0',
   ),
   do3 = device('nicos.devices.vendor.caress.EKFMotor',
                   description = 'beam limiter bottom blade',
                   visibility = (),
                   abslimits = (-145, 145),
                   nameserver = '%s' % nameservice,
                   objname = '%s' % servername_ST169,
                   config = 'DO3_DI 114 11 0x00f1d000 4 -10243 2048 256 2 24 '
                           '100 1 0 1 5000 10 50 0 0 0',
   ),
   le3 = device('nicos.devices.vendor.caress.Motor',
                 description = 'beam limiter left blade',
                 visibility = (),
                 abslimits = (-35, 45),
                 nameserver = '%s' % nameservice,
                 objname = '%s' % servername_ST222,
                 config = 'LE3_DI 500 172.16.1.3:/st222.caress_object '
                          'CopleyStepnet 7 -20000 BeckhoffKL5001 BK5120/63/32/0/0 -10240 -375563',
                 loadblock = loadblock_LE3,
   ),
   ri3 = device('nicos.devices.vendor.caress.Motor',
                  description = 'beam limiter right blade',
                  visibility = (),
                  abslimits = (-35, 45),
                  nameserver = '%s' % nameservice,
                  objname = '%s' % servername_ST222,
                  config = 'RI3_DI 500 172.16.1.3:/st222.caress_object '
                          'CopleyStepnet 8 -20000 BeckhoffKL5001 BK5120/63/32/4/0 -10240 368362',
                  loadblock = loadblock_RI3,
   ),
   slit_3 = device('nicos.devices.generic.slit.Slit',
                  description = 'slit 3',
                  left = 'le3',
                  right = 'ri3',
                  top = 'up3',
                  bottom = 'do3',
                  opmode = 'offcentered',
                  coordinates = 'opposite',
                  fmtstr = '%.2f',
                  unit = 'mm',
   ),
)
