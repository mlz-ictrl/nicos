description = 'sample table rotations'

group = 'lowlevel'

includes = []

servername = 'VMESPODI'

nameservice = 'spodictrl.spodi.frm2'

# caress@spodictrl:/opt/caress>./dump_u1 bls
# BLS: OMGS=(-360,360) TTHS=(-3.1,160)
# XS=(-15,15) YS=(-15,15) ZS=(-20,20)
# SOF: OMGS=-2735.92 TTHS=-1044.04
# XS=0 YS=0 ZS=0


devices = dict(
    tthsm = device('devices.vendor.caress.Motor',
                   description = 'HWB TTHS',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   coderoffset = 1044.04,
                   abslimits = (-3.1, 160),
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
                  precision = 0.001,
                  maxtries = 10,
                 ),
    omgsm = device('devices.vendor.caress.Motor',
                   description = 'HWB OMGS',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   coderoffset = 2735.92,
                   abslimits = (-360, 360),
                   nameserver = '%s' % (nameservice,),
                   objname = '%s' % (servername),
                   config = 'OMGS 114 11 0x00f1c000 2 4096 8000 200 2 24 50 1'
                           ' 0 1 3000 1 10 10 0 1000',
                   lowlevel = True,
                  ),
    omgs = device('devices.generic.Axis',
                  description = 'HWB TTHS',
                  motor = 'omgsm',
                  coder = 'omgsm',
                  precision = 0.005,
                 ),
# ;Sample translation
#   xs = device('devices.vendor.caress.Motor',
#               description = 'HWB XS',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = 0,
#               abslimits = (-15, 15),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'XS 115 11 0x00f1c000 4 3200 6000 200 1 0 50 '
#                        '-1 0 1 5300 1 10 10 0 500',
#              ),
#   ys = device('devices.vendor.caress.Motor',
#               description = 'HWB YS',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = 0,
#               abslimits = (-15, 15),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'YS 115 11 0x00f1e000 2 3200 6000 200 1 0 50 '
#                        '1 0 1 5300 1 10 10 0 500',
#              ),
#   zs = device('devices.vendor.caress.Motor',
#               description = 'HWB ZS',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = 0,
#               abslimits = (-20, 20),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'ZS 115 11 0x00f1e000 3 5000 1000 100 1 0 50 '
#                        '-1 0 1 4000 1 10 10 0 500',
#              ),
)

alias_config = {
}

startupcode = """
"""
