description = 'Radialcollimator CARESS HWB xDevices'

group = 'optional'

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    mot1 = device('nicos.devices.vendor.caress.EKFMotor',
                  description = 'RadColli=ZE',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 0,
                  abslimits = (-8, 8),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'MOT1 115 11 0x00f1d000 4 4050 1000 100 1 0 0 0 0 1 '
                           '5000 1 10 0 0 0',
                  #config = 'MOT1 114 11 0x00f1d000 4 4096 1000 100 2 24 50 1 0 1 '
                  #         '3000 1 10 0 0 0',
                 ),
    rad_fwhm = device('nicos.devices.generic.ManualMove',
                      description = 'FWHM Radialcollimator',
                      fmtstr = '%.1f',
                      default = 5,
                      unit = 'mm',
                      abslimits = (0, 20),
                      requires =  {'level': 'admin',},
                     ),
)
