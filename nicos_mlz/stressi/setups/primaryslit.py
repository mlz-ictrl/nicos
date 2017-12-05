description = 'Primary slit CARESS HWB Devices'

group = 'lowlevel'

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    pst = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'HWB PST',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = -2056.44,
                 abslimits = (-15, 15),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PST 114 11 0x00f1f000 2 2044 500 50 2 24 50 -1 0 1 '
                          '3000 1 10 0 0 0',
                 ),
    psz = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'HWB PSZ',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = -8209.31,
                 abslimits = (-15, 15),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PSZ 114 11 0x00f1f000 1 2044 500 50 2 24 50 -1 0 1 '
                          '3000 1 10 0 0 0',
                 ),
)
