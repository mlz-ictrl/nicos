description = 'sample table rotations'

group = 'lowlevel'

includes = []

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

devices = dict(
    tths = device('nicos.devices.generic.Axis',
                  description = 'HWB TTHS',
                  motor = device('nicos.devices.vendor.caress.Motor',
                                 fmtstr = '%.3f',
                                 unit = 'deg',
                                 coderoffset = 1044.04,
                                 abslimits = (-1.5, 60),
                                 nameserver = '%s' % (nameservice,),
                                 objname = '%s' % (servername),
                                 config = 'TTHS 114 11 0x00f1c000 1 8192 16000'
                                          ' 200 2 25 50 1 1 1 3000 1 10 10 0 '
                                          '1000',
                                ),
                  precision = 0.005,
                  maxtries = 10,
                 ),
    omgs = device('nicos.devices.generic.Axis',
                  description = 'HWB OMGS',
                  motor = device('nicos.devices.vendor.caress.Motor',
                                 fmtstr = '%.2f',
                                 unit = 'deg',
                                 coderoffset = 2735.92,
                                 abslimits = (-730, 730),
                                 nameserver = '%s' % (nameservice,),
                                 objname = '%s' % (servername),
                                 config = 'OMGS 114 11 0x00f1c000 2 4096 8000 '
                                          '200 2 24 50 1 0 1 3000 1 10 10 0 '
                                          '1000',
                               ),
                  precision = 0.005,
                 ),
)

alias_config = {
}
