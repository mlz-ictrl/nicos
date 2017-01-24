description = 'sample table rotations'

group = 'lowlevel'

includes = []

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

devices = dict(
    tthsm  = device('devices.vendor.caress.Motor',
                    description = 'HWB TTHS motor',
                    fmtstr = '%.3f',
                    unit = 'deg',
                    coderoffset = 1044.04,
                    abslimits = (-1.5, 60),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'TTHS 114 11 0x00f1c000 1 8192 16000 200 2 25 50 1'
                             ' 1 1 3000 1 10 10 0 1000',
                    lowlevel = True,
                   ),
    tths = device('devices.generic.Axis',
                  description = 'HWB TTHS',
                  motor = 'tthsm',
                  coder = 'tthsm',
                  precision = 0.005,
                  maxtries = 10,
                  abslimits = (-1.5, 60),
                 ),
    omgsm  = device('devices.vendor.caress.Motor',
                    description = 'HWB OMGS motor',
                    fmtstr = '%.2f',
                    unit = 'deg',
                    coderoffset = 2735.92,
                    abslimits = (-730, 730),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'OMGS 114 11 0x00f1c000 2 4096 8000 200 2 24 50 1'
                           ' 0 1 3000 1 10 10 0 1000',
                    lowlevel = True,
                   ),
    omgs = device('devices.generic.Axis',
                  description = 'HWB OMGS',
                  fmtstr = '%.2f',
                  motor = 'omgsm',
                  coder = 'omgsm',
                  precision = 0.005,
                 ),
)

alias_config = {
}
