description = 'sample table setup'

group = 'lowlevel'
excludes = ['sampletable_1']

nameservice = '172.16.1.1'
servername = 'NVMEV6'

devices = dict(
    z=device('nicos.devices.generic.manual.ManualMove',
             description='vertical manual movement',
             unit='mm',
             abslimits=(0, 50),  # a verificar
             ),
    y=device('nicos.devices.generic.manual.ManualMove',
             description='horizontal manual movement',
             unit='mm',
             abslimits=(0, 90),
             ),
    high_s=device('nicos.devices.vendor.caress.EKFMotor',
                  description='sample table height calibration',
                  fmtstr='%.2f',
                  unit='mm',
                  abslimits=(-160, 20),
                  nameserver='%s' % nameservice,
                  objname='%s' % servername,
                  config='HIGH_S	115	11	0x00f1f000  3    5000	512   32     1     0     0        0    0     1    5000  10   50 0 0 -500',
                  ),
)
