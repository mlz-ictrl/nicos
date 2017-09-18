#  -*- coding: utf-8 -*-

description = 'Monoturm, everything inside the Monochromator housing'

group = 'lowlevel'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

# channel 1   2   3   4   5   6   7   8
#         ca1 mgx mtx mty mth mtt ms1 saph
#                                    saphire is in saph setup
#         ca1 is in collimators setup

# eases address settings: 0x5.. = stepper, 0x6.. = poti, 0x7.. = coder ; .. = channel
MOTOR = lambda x: 0x50 + x
POTI = lambda x: 0x60 + x
CODER = lambda x: 0x70 + x

# eases confbyte settings for IPC-coder cards:
ENDAT = 0x80
SSI = 0

GRAY = 0x40
BINARY = 0

P_NONE = 0x20
P_EVEN = 0

TOTALBITS = lambda x: x & 0x1f


devices = dict(
    bus5 = device('nicos.devices.vendor.ipc.IPCModBusTango',
            tangodevice = tango_base + 'ipc/mono',
            bustimeout = 0.1,
            loglevel = 'info',
            lowlevel = True,
    ),

    #~ # MFH is first device and has 1 stepper, 0 poti, 0 coder and maybe 1 something else (resolver)
#~   mfh_step = device('nicos.devices.vendor.ipc.Motor',
                    #~ bus = 'bus5',
                    #~ addr = MOTOR(1),
                    #~ slope = 900*24*2/360,       # 900:1 gear, 24 steps per rev, 36ßdeg per rev
                    #~ unit = 'deg',
                    #~ abslimits = (-400,400),
                    #~ zerosteps = 500000,
                    #~ confbyte = 8,
                    #~ speed = 30, # default 50, seems to lose steps at 50, reduced to 30
                    #~ accel = 150,
                    #~ microstep = 2,
                    #~ startdelay = 0,
                    #~ stopdelay = 0,
                    #~ ramptype = 1,
                    #~ #power = 0,
                    #~ lowlevel = True,
                    ##~ current = 0.2,
                   #~ ),
#~   mfh_poti = device('nicos.devices.vendor.ipc.Coder',
                    #~ bus = 'bus5',
                    #~ addr = POTI(1),
                    #~ slope = 1,
                    #~ zerosteps = 0,
                    #~ unit = 'deg',
                    #~ lowlevel = True,
                   #~ ),
##~ mfh = device('nicos.devices.generic.Axis',
#~   mfh = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
               #~ motor = 'mfh_step',
               #~ coder = 'mfh_step',
               #~ obs = [],
               #~ precision = 1,
               #~ refpos = 168.75+40,
               #~ refspeed = 5,
               #~ autoref = -10, # autoref every 10 full turns
               ##~ rotary = True,
              #~ ),

    #
    # MGX is second device and has 1 stepper, 1 poti, 0 coder
    # endschalter+=599620 steps,poti=852 ca. 3.1 deg
    # 0 = 500000 steps, poti=2259
    # endschalter-=398852, poti=3727 ca 3.16 deg
    mgx_step = device('nicos_mlz.panda.devices.ipc.Motor',
                      bus = 'bus5',
                      addr = MOTOR(2),
                      slope = 32000,
                      unit = 'deg',
                      abslimits = (-3, 3),
                      zerosteps = 500000,
                      speed = 50,
                      accel = 24,
                      microstep = 16,
                      divider = 4,
                      lowlevel = True,
                      #~ current = 1.5,
                     ),
    mgx_poti = device('nicos.devices.vendor.ipc.Coder',
                      bus = 'bus5',
                      addr = POTI(2),
                      slope = -459.16,
                      zerosteps = 2259,
                      unit = 'deg',
                      lowlevel = True,
                     ),
    mgx = device('nicos.devices.generic.Axis',
                 description = 'mono tilt (up/down)',
                 motor = 'mgx_step',
                 coder = 'mgx_step',
                 obs = ['mgx_poti'],
                 precision = 0.01,
                ),

    #
    # MTX is third device and has 1 stepper, 1 poti, 0 coder
    # endschalter- =248643 steps, poti=0, ca 15.7mm
    # 0 = 500000 steps, poti=3910
    # endschalter+ 553200= steps, poti=4790, ca -3.3mm
    mtx_step = device('nicos_mlz.panda.devices.ipc.Motor',
                      bus = 'bus5',
                      addr = MOTOR(3),
                      slope = 16000,
                      unit = 'mm',
                      abslimits = (-15,3),
                      zerosteps = 500000,
                      speed = 50,
                      accel = 24,
                      microstep = 16,
                      divider = 4,
                      lowlevel = True,
                      #~ current = 1.5,
                     ),
    mtx_poti = device('nicos.devices.vendor.ipc.Coder',
                      bus = 'bus5',
                      addr = POTI(3),
                      slope = 265.25,
                      zerosteps = 3910,
                      unit = 'mm',
                      lowlevel = True,
                     ),
    mtx = device('nicos.devices.generic.Axis',
                 description = 'mono translation (left/right) (needed for Si!)',
                 motor = 'mtx_step',
                 coder = 'mtx_step',
                 precision = 0.1,
                 obs = ['mtx_poti'],
                 fmtstr = '%.1f',
                ),

    #
    # MTY is fourth device and has 1 stepper, 1 poti, 0 coder
    # endschalter- steps=684692, poti= 862, 11.5mm
    # 0 500000 steps, poti=3940
    # endschalter+ = 294059, poti=7436, -12.8mm
    mty_step = device('nicos_mlz.panda.devices.ipc.Motor',
                      bus = 'bus5',
                      addr = MOTOR(4),
                      slope = -16000,
                      unit = 'mm',
                      abslimits = (-11,11),
                      zerosteps = 500000,
                      speed = 200,
                      accel = 24,
                      microstep = 16,
                      divider = 4,
                      lowlevel = True,
                      #~ current = 1.5,
                     ),
    mty_poti = device('nicos.devices.vendor.ipc.Coder',
                      bus = 'bus5',
                      addr = POTI(4),
                      slope = 269.2655,
                      zerosteps = 3940,
                      unit = 'mm',
                      lowlevel = True,
                     ),
    mty = device('nicos.devices.generic.Axis',
                 description = 'mono translation along Y (thickness correction)',
                 motor = 'mty_step',
                 coder = 'mty_step',
                 obs = ['mty_poti'],
                 precision = 0.1,
                 fmtstr = '%.1f',
                ),

    #
    # MTH is fith device and has 1 stepper, 0 poti, 1 coder
    mth_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus5',
                      addr = MOTOR(5),
                      slope = -8000,
                      unit = 'deg',
                      abslimits = (-25,100),
                      zerosteps = 800000,
                      speed = 200,
                      accel = 24,
                      microstep = 8,
                      divider = 4,
                      lowlevel = True,
                      #~ current = 1.5,
                     ),
    mth_enc = device('nicos.devices.vendor.ipc.Coder',
                     bus = 'bus5',
                     addr = CODER(5),
                     slope = -2**26 / 360.0,
                     zerosteps = 52095568,
                     confbyte = ENDAT | BINARY | P_EVEN | TOTALBITS(26),
                     unit = 'deg',
                     circular = -360, # map values to -180..0..180 degree
                     lowlevel = True,
                    ),
    mth = device('nicos.devices.generic.Axis',
                 description = 'rocking angle of monochromator',
                 motor = 'mth_step',
                 coder = 'mth_enc',
                 obs = [],
                 precision = 0.01,
                 #offset = -0.0726863,
                 offset = -0.0926863,
                ),

    #
    # MTT is sixth device and has 0 stepper, 0 poti, 1 coder
    mtt_enc = device('nicos.devices.vendor.ipc.Coder',
                     description = 'rotary encoder on bottom of mtt',
                     bus = 'bus5',
                     addr = CODER(6),
                     slope = 2**26 / 360.0,
                     zerosteps = 50705250,
                     confbyte = ENDAT | BINARY | P_EVEN | TOTALBITS(26),
                     unit = 'deg',
                     circular = -360, # map values to -180..0..180 degree
                     lowlevel = True,
                    ),

    #
    # MS1 is seventh device and has 1 stepper, 0 poti, 1 coder
    ms1_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus5',
                   #~ addr = MOTOR(7), #original
                      addr = MOTOR(6),        #test
                      slope = -1600 / 3.0,
                      unit = 'mm',
                      abslimits = (-1.0, 51.0),
                      zerosteps = 500000,
                   #~ refpos = 496587,
                   #~ refswitch = 'low',
                      speed = 200,
                      accel = 8,
                      divider = 4,
                      microstep = 16,
                      lowlevel = True,
                     ),
    ms1_enc = device('nicos.devices.vendor.ipc.Coder',
                     bus = 'bus5',
                     addr = CODER(8),
                     slope = 2**13 / 3.0,        # one full turn every 3mm, encoder is 14bit turns+12 bit per turn
                     zerosteps = 555555,
                     confbyte = SSI | BINARY | P_NONE | TOTALBITS(26),
                     unit = 'mm',
                     lowlevel = True,
                    ),
    ms1 = device('nicos.devices.generic.Axis',
                 description = 'primary horizontal slit before mono',
                 userlimits = (0, 50),
                 motor = 'ms1_step',
                 coder = 'ms1_enc',
                 obs = [],
                 precision = 0.05,
                 fmtstr = '%.1f',
                ),

    #
    # MFV is eigth device and has 1 stepper, 0 poti, 0 coder and maybe 1 something else (resolver)
#~   mfv_step = device('nicos.devices.vendor.ipc.Motor',
                    #~ bus = 'bus5',
                    #~ addr = MOTOR(8),
                    #~ slope = 900*24*2/360,       # 900:1 gear, 24 steps per rev, 36ßdeg per rev
                    #~ unit = 'deg',
                    #~ abslimits = (-400,400),
                    #~ zerosteps = 500000,
                    #~ confbyte = 8,
                    #~ speed = 50,
                    #~ accel = 8,
                    #~ #power = 0,
                    ##current = 0.2,
                    #~ lowlevel = True,
                   #~ ),
#~   mfv_poti = device('nicos.devices.vendor.ipc.Coder',
                    #~ bus = 'bus5',
                    #~ addr = POTI(8),
                    #~ slope = 1,
                    #~ zerosteps = 0,
                    #~ unit = 'deg',
                    #~ lowlevel = True,
                   #~ ),
##~   mfv = device('nicos.devices.generic.Axis',
#~   mfv = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
               #~ motor = 'mfv_step',
               #~ coder = 'mfv_step',
               #~ obs = [],
               #~ precision = 1,
               #~ refpos = 221.3,
               #~ refspeed = 5,
               #~ autoref = -10, # autoref every 10 full turns
               ##rotary = True,
              #~ ),

)
