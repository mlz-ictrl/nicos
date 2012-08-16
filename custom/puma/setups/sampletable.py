#  -*- coding: utf-8 -*-

name = 'Sampletable complete'

includes = ['system']
 
 # sth,stt,sgx,sgy,stx,sty,stz,--

devices = dict(
    motorbus4 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='puma/rs485/s43',
            timeout=0.5,
    ),
    motorbus1 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='puma/rs485/mc',
            timeout=0.5,
    ),
     
    # STT is first device and has 1 stepper, 0 poti, 1 coder
    st_phi = device('nicos.ipc.Motor',
            bus = 'motorbus4',
            addr = 53,
            slope = 400,
            unit = 'deg',
            abslimits = (-5, 114.1),
            zerosteps = 500000,
            #confbyte = 8,
            #speed = 100,
            #accel = 150,
            #microstep = 16,
            #startdelay = 0.2,
            #stopdelay = 0.1,
            #ramptype = 1,
            lowlevel = True,
    ),
    co_phi = device('nicos.ipc.Coder',
            bus = 'motorbus1',
            addr = 128,
            slope = -186413.5111,
            zerosteps = 9392590,
            #confbyte = 148,
            unit = 'deg',
            #circular = -360, # map values to -180..0..180 degree
            lowlevel = True,
    ),
    phi = device('nicos.generic.Axis',
            motor = 'st_phi',
            coder = 'co_phi',
            obs = [],
            precision = 0.005,
            offset = 0.540,
    ),
)
