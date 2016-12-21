description = 'Tensile machine (CORBA) setup'

group = 'optional'

servername = 'SPODICTRL'

nameservice = 'spodisrv.spodi.frm2'

includes = []

# caress@spodictrl:/opt/caress>./dump_u1 bls
# BLS: OMGS=(-360,360) TTHS=(-3.1,160) OMGM=(40,80) CHIM=(-3,3) XM=(-15,15)
# YM=(-15,15) ZM=(0,220) SLITM_U=(-31,85) SLITM_D=(-85,31) SLITM_L=(-15.2,15.2)
# SLITM_R=(-15.2,15.2) SLITS_U=(0,45) SLITS_D=(-45,0) SLITS_L=(-15,0)
# SLITS_R=(0,15) POSH=(0,78) EXT=(-5,5) LOAD=(-50000,50000) CHIT=(-180,180)
# TEPOS=(-20,50) TEEXT=(-1000,3000) TELOAD=(-50000,50000) TOPOS=(-360,360)
# TOMOM=(1000,1000) SAMS=(-360,360) SAMR=(-360,360) XS=(-15,15) YS=(-15,15)
# ZS=(-20,20)
# SOF: OMGS=-2735.92 TTHS=-1044.04 OMGM=-792.677 CHIM=2928.3 XM=-5852.43
# YM=-2043.89 ZM=-6347.84 SLITM_U=0 SLITM_D=0 SLITM_L=0 SLITM_R=0 SLITS_U=0
# SLITS_D=0 SLITS_L=0 SLITS_R=0 POSH=0 EXT=0 LOAD=0 CHIT=0 TEPOS=0 TEEXT=0
# TELOAD=0 TOPOS=0 TOMOM=0 SAMS=38573.1 SAMR=0 XS=0 YS=0 ZS=0

devices = dict(
    tepos = device('devices.vendor.caress.Motor',
                  description = 'HWB TEPOS',
                  fmtstr = '%.2f',
                  unit = 'mm',
                  coderoffset = 0,
                  abslimits = (-20, 50),
                  nameserver = '%s' % (nameservice,),
                  config = 'TEPOS 500 TensilePos.ControllableDevice',
                 ),
    teload = device('devices.vendor.caress.Motor',
                    description = 'HWB TELOAD',
                    fmtstr = '%.2f',
                    unit = 'N',
                    coderoffset = 0,
                    abslimits = (-50000, 50000),
                    nameserver = '%s' % (nameservice,),
                    config = 'TELOAD 500 TensilePos.ControllableDevice',
                   ),
    teext = device('devices.vendor.caress.Motor',
                   description = 'HWB TEEXT',
                   fmtstr = '%.2f',
                   unit = 'mm',
                   coderoffset = 0,
                   abslimits = (-1000, 3000),
                   nameserver = '%s' % (nameservice,),
                   config = 'TEEXT 500 TensilePos.ControllableDevice',
                  ),
    topos = device('devices.vendor.caress.Motor',
                   description = 'HWB TOPOS',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   coderoffset = 0,
                   abslimits = (-360, 360),
                   nameserver = '%s' % (nameservice,),
                   config = 'TOPOS 500 TensilePos.ControllableDevice',
                  ),
    tomom = device('devices.vendor.caress.Motor',
                   description = 'HWB TOMOM',
                   fmtstr = '%.2f',
                   unit = 'mm',
                   coderoffset = 0,
                   abslimits = (1000, 1000),
                   nameserver = '%s' % (nameservice,),
                   config = 'TOMOM 500 TensilePos.ControllableDevice',
                  ),
    chit = device('devices.vendor.caress.Motor',
                  description = 'HWB CHIT',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 0,
                  abslimits = (-180, 180),
                  nameserver = '%s' % (nameservice,),
                  objname = 'VMESPODI',
                  config = 'CHIT 115 11 0x00f1d000 1 22500 6000 50 1 0 0 '
                           '1 0 1 3000 1 10 0 0 0',
                 ),
)

alias_config = {
}
