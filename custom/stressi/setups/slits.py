description = 'Primary slit CARESS HWB Devices'

group = 'lowlevel'

servername = 'VME'

nameservice = 'stressictrl'

includes = ['mux']

# SOF: OMGS=-2048 TTHS=-3319.25 PHIS=-7380.47 CHIS=1114.74 OMGM=0 TTHM=0 TRANSM=0
# XT=1033.53 YT=10242.9 ZT=1022 XE=0 YE=0 ZE=0 PSZ=0 PSW=0 PSH=0 PST=0 SST=0
# MOT1=0 M1_CHI=0 M1_FOC=0 M1_TR=0 M2_CHI=0 M2_FOC=0 M2_TR=0 M3_CHI=0 M3_FOC=0
# M3_TR=0 SLITE=0 SLITM_H=0 SLITM_W=0 SLITS_U=0 SLITS_D=0 SLITS_L=0 SLITS_R=0
# YSD=0 CHIN=0 PHIN=0 ROBX=0 ROBY=0 ROBZ=0 ROBA=0 ROBB=0 ROBC=0 ROBJ1=0 ROBJ2=0
# ROBJ3=0 ROBJ4=0 ROBJ5=0 ROBJ6=0 ROBT=0 ROBS=0 ROBSJ=0 ROBSL=0 ROBSR=0 TTHR=0
# OMGR=0 CHIR=0 PHIR=0 XR=0 YR=0 ZR=0
# caress@stressictrl:~>dump_u1 bls
# BLS: OMGS=(-200,200) TTHS=(20,130) PHIS=(-720,720) CHIS=(-5,100) OMGM=(-200,200)
# TTHM=(-200,200) TRANSM=(-200,200) XT=(-120,120) YT=(-120,120) ZT=(0,300)
# XE=(-200,200) YE=(-200,200) ZE=(-200,200) PSZ=(-15,15) PSW=(0,10) PSH=(0,17)
# PST=(-15,15) SST=(-100,100) MOT1=(-200,200) M1_CHI=(-600,600) M1_FOC=(0,4096)
# M1_TR=(-600,600) M2_CHI=(-600,600) M2_FOC=(0,4096) M2_TR=(-600,600)
# M3_CHI=(-600,600) M3_FOC=(0,4096) M3_TR=(-600,600) SLITE=(0,70) SLITM_H=(0,155)
# SLITM_W=(0,100) SLITS_U=(-10,43) SLITS_D=(-43,10) SLITS_L=(-26,10)
# SLITS_R=(-10,26) YSD=(30,2000) CHIN=(-1,91) PHIN=(-720,720) ROBX=(-2000,2000)
# ROBY=(-2000,2000) ROBZ=(-2000,2000) ROBA=(-180,180) ROBB=(-360,360)
# ROBC=(-720,720) ROBJ1=(-160,160) ROBJ2=(-137.5,137.5) ROBJ3=(-150,150)
# ROBJ4=(-270,270) ROBJ5=(-105,120) ROBJ6=(-15000,15000) ROBT=(0,1000)
# ROBS=(0,1000) ROBSJ=(0,20) ROBSL=(0,100) ROBSR=(0,50) TTHR=(0,140) OMGR=(0,140)
# CHIR=(-180,180) PHIR=(-720,720) XR=(-2000,2000) YR=(-2000,2000) ZR=(-2000,2000)

devices = dict(
    slits_u = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITS_U',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = -0,
                     abslimits = (-10, 43),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITS_U 39 3 1 13 100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slits_d = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITS_D',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (-43, 10),
                     userlimits = (-43, 10),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITS_D 39 3 1 14 -100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slits_l = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITS_L',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (-26, 10),
                     userlimits = (-26, 10),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITS_L 39 3 1 15 -100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slits_r = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITS_R',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (-10, 26),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITS_R 39 3 1 16 100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slits = device('stressi.slit.Slit',
                   description = 'sample slit 4 blades',
                   left = 'slits_l',
                   right = 'slits_r',
                   bottom = 'slits_d',
                   top = 'slits_u',
                   opmode = 'centered',
                   pollinterval = 60,
                   maxage = 90,
                  ),
    slitm_w = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITM_W',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (0, 100),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITM_W 39 3 1 10 100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slitm_h = device('devices.vendor.caress.MuxMotor',
                     description = 'HWB SLITM_H',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     coderoffset = 0,
                     abslimits = (0, 155),
                     nameserver = '%s' % (nameservice,),
                     objname = '%s' % (servername),
                     config = 'SLITM_H 39 3 1 11 100.0 20 80',
                     lowlevel = True,
                     pollinterval = 60,
                     maxage = 90,
                     mux = 'mux',
                    ),
    slitm = device('stressi.slit.TwoAxisSlit',
                   description = 'Monochromator entry slit',
                   horizontal = 'slitm_w',
                   vertical = 'slitm_h',
                   pollinterval = 60,
                   maxage = 90,
                  ),
    slite = device('devices.vendor.caress.MuxMotor',
                   description = 'HWB SLITE',
                   fmtstr = '%.2f',
                   unit = 'mm',
                   coderoffset = 0,
                   abslimits = (0, 70),
                   nameserver = '%s' % (nameservice,),
                   objname = '%s' % (servername),
                   config = 'SLITM_E 39 3 1 12 100.0 20 80',
                   pollinterval = 60,
                   maxage = 90,
                   mux = 'mux',
                  ),
)
