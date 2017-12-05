description = 'Sample table CARESS HWB Devices'

group = 'lowlevel'

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

includes = ['aliases']

devices = dict(
    tths_s = device('nicos.devices.vendor.caress.EKFMotor',
                  description = 'HWB TTHS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 3319.25,
                  abslimits = (20, 130),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'TTHS 114 11 0x00f1c000 3 4096 500 5 2 24 50 1 10 1'
                           ' 3000 1 30 0 0 0',
                  lowlevel = True,
                 ),
    omgs_s = device('nicos.devices.vendor.caress.EKFMotor',
                  description = 'HWB OMGS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 2048,
                  abslimits = (-360, 360),
                  userlimits = (-200, 200),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'OMGS 114 11 0x00f1c000 1 4096 2048 200 2 24 50 1 0'
                           ' 1 3000 1 10 0 0 0',
                  lowlevel = True,
                 ),
    xt_s = device('nicos.devices.vendor.caress.EKFMotor',
                description = 'HWB XT',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = -1033.53,
                abslimits = (-1000, 1000),
                userlimits = (-120, 120),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'XT 114 11 0x00f1d000 1 8192 10000 1000 2 24 100'
                         ' -1 0 1  5000 1 10 0 0 0',
                lowlevel = True,
               ),
    yt_s = device('nicos.devices.vendor.caress.EKFMotor',
                description = 'HWB YT',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = -10242.9,
                abslimits = (-1000, 1000),
                userlimits = (-120, 120),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'YT 114 11 0x00f1d000 3 819 10000 1000 2 24 100'
                         ' -1 0 1 5000 1 10 0 0 0',
                lowlevel = True,
               ),
    zt_s = device('nicos.devices.vendor.caress.EKFMotor',
                description = 'HWB ZT',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = -1022,
                abslimits = (-1000, 1000),
                userlimits = (-0, 300),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'ZT 114 11 0x00f1e000 1 16384 10000 1000 2 24 100'
                         ' -1 0 1 5000 1 10 0 0 0',
                lowlevel = True,
               ),
)

alias_config = {
    'tths':  {'tths_s': 200,},
    'omgs': {'omgs_s': 200,},
    'xt': {'xt_s': 200,},
    'yt': {'yt_s': 200,},
    'zt': {'zt_s': 200,},
}
