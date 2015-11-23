description = 'Detector CARESS HWB Devices'

group = 'lowlevel'

servername = 'STRESSICTRL'

nameservice = 'stressictrl'

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


# ;MESYTEC PSD histogram (2D)
# ;name   kind    bus     		  ignore  	  ignore  xchan   ychan   yheight(mm)
# ;LDET   500     qmesydaq.caress_object  diffractogram   0       256     80
# ;LDET   500     qmesydaq.caress_object  spectrogram     0       80      all
# ADET    500     qmesydaq.caress_object  histogram       0       256     256
# ;ADET   500     qmesydaq.caress_object  histogram       0       1024    1024
# MON     500     qmesydaq.caress_object  monitor1
# ;MON2   500     qmesydaq.caress_object  monitor2
# ;                                               Hz
# TIM1    500     qmesydaq.caress_object  timer   1
# ;EVENT  500     qmesydaq.caress_object  event

devices = dict(
    mon = device('devices.vendor.caress.Counter',
                 description = 'HWB MON',
                 fmtstr = '%d',
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'MON 500 qmesydaq.caress_object monitor1',
                ),
    tim1 = device('devices.vendor.caress.Timer',
                  description = 'HWB TIM1',
                  fmtstr = '%.2f',
                  unit = 's',
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'TIM1 500 qmesydaq.caress_object timer 1',
                 ),
#   tim2 = device('devices.vendor.caress.Timer',
#                 description = 'HWB TIM2',
#                 fmtstr = '%.2f',
#                 unit = 's',
#                 nameserver = '%s' % (nameservice,),
#                 objname = '%s' % (servername),
#                 config = 'TIM2 116 11 0x1000000 3',
#                ),
#   adet = device('devices.vendor.caress.MultiChannelDetector',
#                 description = 'HWB ADET',
#                 timer = 'tim1',
#                 monitors = ['mon'],
#                 counters = ['tim2'],
#                 maxage = 3,
#                 pollinterval = 0.5,
#                 nameserver = '%s' % (nameservice,),
#                 objname = '%s' % (servername),
#                 config = 'ADET 500 qmesydaq.caress_object histogram 0 256 '
#                          '256',
#                ),
    ysd = device('devices.generic.ManualMove',
                 description = 'Distance detector to sample',
                 fmtstr = '%.1f',
                 default = 1050,
                 unit = 'mm',
                 abslimits = (700, 1700),
                ),
)
