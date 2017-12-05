description = 'STRESS-SPEC setup with Huber Eulerian cradle plus small xyz table'

group = 'basic'

includes = ['system','eulerian_huber',  'mux', 'monochromator', 'detector', 'sampletable',
            'primaryslit', 'slits', 'reactor']

excludes = ['eulerian_newport', 'eulerian_tensile', 'robot', 'primaryslit_huber']

sysconfig = dict(
    datasinks = ['caresssink'],
)

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    xe =      device('nicos.devices.vendor.caress.EKFMotor',
                     description = 'HWB XE',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (-80, 80),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'XE 115 11 0x00f1c000 4 50 1000 100 1 0 0 0 0 1'
                              ' 5000 1 10 0 0 0',
                    ),
    ye =      device('nicos.devices.vendor.caress.EKFMotor',
                     description = 'HWB YE',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (-80, 80),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'YE 115 11 0x00f1d000 2 50 1000 100 1 0 0 0 0 1 '
                              '5000 1 10 0 0 0',
                    ),
    ze =      device('nicos.devices.vendor.caress.EKFMotor',
                     description = 'HWB ZE',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (0, 20),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'ZE 115 11 0x00f1f000 4 200 1000 100 1 0 0 0 0 1 '
                              '5000 1 10 0 0 0',
                    ),
)
