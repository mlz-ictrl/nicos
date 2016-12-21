description = 'sample tranlation Z'

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
    zs = device('devices.vendor.caress.Motor',
                description = 'HWB ZS',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = 0,
                abslimits = (-20, 20),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'ZS 115 11 0x00f1e000 3 5000 1000 100 1 0 50 '
                         '-1 0 1 4000 1 10 10 0 500',
               ),
)

alias_config = {
}
