description = 'sample translation XY'

group = 'optional'

includes = []

servername = 'VMESPODI'

nameservice = 'spodisrv'

# caress@spodictrl:/opt/caress>./dump_u1 bls
# BLS: OMGS=(-360,360) TTHS=(-3.1,160)
# XS=(-15,15) YS=(-15,15) ZS=(-20,20)
# SOF: OMGS=-2735.92 TTHS=-1044.04
# XS=0 YS=0 ZS=0


devices = dict(
    xs = device('devices.vendor.caress.Motor',
                description = 'HWB XS',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = 0,
                abslimits = (-15, 15),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'XS 115 11 0x00f1c000 4 3200 6000 200 1 0 50 '
                         '-1 0 1 5300 1 10 10 0 500',
               ),
    ys = device('devices.vendor.caress.Motor',
                description = 'HWB YS',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = 0,
                abslimits = (-15, 15),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'YS 115 11 0x00f1e000 2 3200 6000 200 1 0 50 '
                         '1 0 1 5300 1 10 10 0 500',
               ),
)

alias_config = {
}
