description = 'Monochromator device setup'

group = 'lowlevel'

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

includes = []

# caress@spodictrl:/opt/caress>./dump_u1 bls
# BLS: OMGM=(40,80) CHIM=(-3,3) XM=(-15,15) YM=(-15,15) ZM=(0,220)
# SOF: OMGM=-792.677 CHIM=2928.3 XM=-5852.43  YM=-2043.89 ZM=-6347.84


devices = dict(
# ;Monochromator
#   omgm = device('devices.vendor.caress.Motor',
#                 description = 'HWB OMGM',
#                 fmtstr = '%.2f',
#                 unit = 'deg',
#                 coderoffset = -792.677,
#                 abslimits = (40, 80),
#                 nameserver = '%s' % (nameservice,),
#                 objname = '%s' % (servername),
#                 config = 'OMGM 114 11 0x00f1c000 3 8192 8000 200 2 25 50 '
#                          '1 0 1 3000 1 10 10 0 1000',
#                ),
#   chim = device('devices.vendor.caress.Motor',
#                 description = 'HWB CHIM',
#                 fmtstr = '%.2f',
#                 unit = 'deg',
#                 coderoffset = 2928.3,
#                 abslimits = (-3, 3),
#                 nameserver = '%s' % (nameservice,),
#                 objname = '%s' % (servername),
#                 config = 'CHIM 114 11 0x00f1e000 1 8192 6000 200 2 25 50 '
#                          '-1 0 1 5300 1 10 10 0 1000',
#                ),
#   zm = device('devices.vendor.caress.Motor',
#               description = 'HWB ZM',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = -6347.84,
#               abslimits = (0, 220),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'ZM 114 11 0x00f1d000 2 4096 6000 200 2 25 50 '
#                        '1 0 1 3360 1 10 10 0 500',
#              ),
#   ym = device('devices.vendor.caress.Motor',
#               description = 'HWB YM',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = -2043.89,
#               abslimits = (-15, 15),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'YM 114 11 0x00f1d000 3 4096 6000 200 2 25 50 '
#                        '1 0 1 5300 1 10 10 0 500',
#              ),
#   xm = device('devices.vendor.caress.Motor',
#               description = 'HWB XM',
#               fmtstr = '%.2f',
#               unit = 'mm',
#               coderoffset = -5852.43,
#               abslimits = (-15, 15),
#               nameserver = '%s' % (nameservice,),
#               objname = '%s' % (servername),
#               config = 'XM 114 11 0x00f1d000 4 4096 6000 200 2 25 50 '
#                        '1 0 1 5300 1 10 10 0 500',
#              ),
)

alias_config = {
}
