#  -*- coding: utf-8 -*-

description = 'Sampletable complete'

includes = ['system']

group = 'lowlevel'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

# BUS 2 (sample table)
# channel  1     2   3   4   5   6   7   8
#        sth_st stt sgx sgy stx sty stz ---

# BUS 4 (spare one)
# channel  1     2   3   4   5   6   7   8
#        sth_st  --- --- --- --- --- --- ca2

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
    bus2 = device('nicos.devices.vendor.ipc.IPCModBusTango',
                  tangodevice = tango_base + 'ipc/sample',
                  bustimeout = 0.1,
                  loglevel = 'info',
                  lowlevel = True,
                 ),

    bus4 = device('nicos.devices.vendor.ipc.IPCModBusTango',
                  tangodevice = tango_base + 'ipc/spare',
                  bustimeout = 0.1,
                  loglevel = 'info',
                  lowlevel = True,
                 ),

    # STT is first device and has 1 stepper, 0 poti, 1 coder
    stt_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(1),
                      slope = 2000,
                      unit = 'deg',
                      abslimits = (-100, 130),
                      zerosteps = 500000,
                      confbyte = 8,
                      speed = 100,
                      accel = 17,
                      microstep = 2,
                      startdelay = 0.2,
                      stopdelay = 0.1,
                      ramptype = 1,
                      lowlevel = True,
                      #~ current = 2.0,
                     ),
    stt_enc = device('nicos.devices.vendor.ipc.Coder',
                     bus = 'bus2',
                     addr = CODER(1),
                     slope = -2**20 / 360.0,
                     zerosteps = 543767,
                     confbyte = ENDAT | BINARY | P_EVEN | TOTALBITS(20),
                     unit = 'deg',
                     circular = -360, # map values to -180..0..180 degree
                     lowlevel = True,
                    ),
    stt = device('nicos.devices.generic.Axis',
                 description = 'sample two theta',
                 motor = 'stt_step',
                 coder = 'stt_enc',
                 obs = [],
                 precision = 0.025,
                 #offset = -0.925,
                 offset = -1.045,
                ),

    # STH is second device and has 1 stepper, 0 poti, 1 coder
    sth_st_step = device('nicos.devices.vendor.ipc.Motor',
                         bus = 'bus4',  #was bus2
                         addr = MOTOR(2),
                         slope = 2000,
                         unit = 'deg',
                         abslimits = (1, 359),
                         zerosteps = 100000,
                         speed = 100,
                         accel = 24,
                         microstep = 2,
                         startdelay = 0,
                         stopdelay = 0,
                         ramptype = 1,
                         lowlevel = True,
                      #~ current = 2.0,
                        ),
    sth_st_enc = device('nicos.devices.vendor.ipc.Coder',
                        bus = 'bus2',
                        addr = CODER(2),
                        slope = -2**20 / 360.0,
                        zerosteps = 831380,
                        confbyte = ENDAT | BINARY | P_EVEN | TOTALBITS(20),
                        unit = 'deg',
                        circular = 360, # map values to -180..0..180 degree
                        lowlevel = True,
                       ),
    sth_st = device('nicos.devices.generic.Axis',
                    description = 'sth mounted on sampletable',
                    motor = 'sth_st_step',
                    coder = 'sth_st_enc',
                    obs = [],
                    precision = 0.02,
                   ),

    # SGX is third device and has 1 stepper, 0 poti, 1 coder
    sgx_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(3),  #original tripple card
                      #addr = MOTOR(8),
                      slope = -3200,
                      unit = 'deg',
                      abslimits = (-15.1, 15.1),
                      zerosteps = 500000,
                      speed = 50,
                      accel = 24,
                      microstep = 16,
                      startdelay = 0,
                      stopdelay = 0,
                      ramptype = 1,
                      lowlevel = True,
                   #~ current = 2.0,
                     ),
    sgx_enc = device('nicos.devices.vendor.ipc.Coder',
                     bus = 'bus4',
                     addr = CODER(3), #original tripple card
                     #addr = CODER(8),
                     slope = -2**13 / 1.0,
                     #zerosteps = 33513471,
                     #zerosteps = 33554406, #33554431,
                     zerosteps = 33546235, #changed 19.3.2015
                     confbyte = SSI | GRAY | P_NONE | TOTALBITS(25),
                     unit = 'deg',
                     circular = -4096,    # 12 bit (4096) for turns, times 2 deg per turn divided by 2 (+/-)
                     lowlevel = True,
                    ),
    sgx = device('nicos.devices.generic.Axis',
                 description = 'sample goniometer around X',
                 motor = 'sgx_step',
                 coder = 'sgx_enc',
                 obs = [],
                 precision = 0.05,
              #~ rotary = True,
                ),

    # SGY is fourth device and has 1 stepper, 0 poti, 1 coder
    sgy_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(4), #original tripple card on bus2
                      #addr = MOTOR(8),
                      slope = 3200,
                      unit = 'deg',
                      abslimits = (-15.1, 15.1),
                      zerosteps = 500000,
                      speed = 50,
                      accel = 24,
                      microstep = 16,
                      startdelay = 0,
                      stopdelay = 0,
                      ramptype = 1,
                      lowlevel = True,
                   #~ current = 2.0,
                     ),
    sgy_enc = device('nicos.devices.vendor.ipc.Coder',
                     bus = 'bus4',
                     addr = CODER(4),  #original tripple card on bus2
                     #addr = CODER(8),
                     slope = 2**13 / 1.0,
                     #zerosteps = 33554387, # 33554410,
                     zerosteps = 8147,  #changed 19.3.2015
                     confbyte = SSI | GRAY | P_NONE | TOTALBITS(25),
                     unit = 'deg',
                     circular = -4096,    # 12 bit (4096) for turns, times 2 deg per turn divided by 2 (+/-)
                     lowlevel = True,
                    ),
    sgy = device('nicos.devices.generic.Axis',
                 description = 'sample goniometer around Y',
                 motor = 'sgy_step',
                 coder = 'sgy_enc',
                 obs = [],
                 precision = 0.05,
              #~ rotary = True,
                ),

    vg1      = device('nicos.devices.tas.VirtualGonio',
                      description = 'Gonio along orient1 reflex',
                      cell = 'Sample',
                      gx = 'sgx',
                      gy = 'sgy',
                      axis = 1,
                      unit = 'deg',
                     ),
    vg2      = device('nicos.devices.tas.VirtualGonio',
                      description = 'Gonio along orient2 reflex',
                      cell = 'Sample',
                      gx = 'sgx',
                      gy = 'sgy',
                      axis = 2,
                      unit = 'deg',
                     ),

    # STX is fith device and has 1 stepper, 1 poti, 0 coder
    stx_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(5),
                      slope = 12800,
                      unit = 'mm',
                      abslimits = (-20, 20),
                      zerosteps = 500000,
                      speed = 100,
                      accel = 24,
                      microstep = 16,
                      lowlevel = True,
                   #~ divider = 4,
                   #~ current = 1.5,
                     ),
    stx_poti = device('nicos.devices.vendor.ipc.Coder',
                      bus = 'bus2',
                      addr = POTI(5),
                     slope = 79.75,
                      zerosteps = 1840.02,
                      unit = 'mm',
                      lowlevel = True,
                     ),
    stx = device('nicos.devices.generic.Axis',
                 description = 'sample translation along X',
                 motor = 'stx_step',
                 coder = 'stx_step',
                 obs = ['stx_poti'],
                 precision = 0.05,
                 fmtstr = '%.1f',
                ),

    # STY is sixth device and has 1 stepper, 1 poti, 0 coder
    sty_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(6),
                      slope = 12800,
                      unit = 'mm',
                      abslimits = (-15, 15),
                      zerosteps = 500000,
                      speed = 100,
                      accel = 24,
                      microstep = 16,
                      lowlevel = True,
                   #~ divider = 4,
                   #~ current = 1.5,
                     ),
    sty_poti = device('nicos.devices.vendor.ipc.Coder',
                      bus = 'bus2',
                      addr = POTI(6),
                      slope = 79.65,
                      zerosteps = 1968.05,
                      unit = 'mm',
                      lowlevel = True,
                     ),
    sty = device('nicos.devices.generic.Axis',
                 description = 'sample translation along Y',
                 motor = 'sty_step',
                 coder = 'sty_step',
                 obs = ['sty_poti'],
                 precision = 0.05,
                 fmtstr = '%.1f',
                ),

    # STZ is seventh device and has 1 stepper, 0 poti, 0 coder
    stz_step = device('nicos.devices.vendor.ipc.Motor',
                      bus = 'bus2',
                      addr = MOTOR(7),
                      slope = 20000,
                      unit = 'mm',
                      abslimits = (-20, 20),
                      zerosteps = 500000,
                      speed = 50,
                      accel = 24,
                      microstep = 2,
                      lowlevel = True,
                   #~ divider = 4,
                   #~ current = 1.5,
                     ),

    stz = device('nicos.devices.generic.Axis',
                 description = 'vertical sample translation',
                 motor = 'stz_step',
                 coder = 'stz_step',
                 obs = [],
                 precision = 0.1,
                 fmtstr = '%.3f',
                 userlimits = (-15, 15),
                ),

    # eigth device is not used yet......

)

alias_config = {
    'sth': {'sth_st': 10},
}
