description = 'TMR vacuum system setup'
group = 'optional'

tango_base = 'tango://phys.tmr.jcns.fz-juelich.de:10000/tmr/'
s7_io = tango_base + 's7_io/plc_'

devices = dict(
    scroll_pump = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = s7_io + 'scroll_pump',
        description = 'Scroll pump.',
        mapping = dict(off=0, on=1),
    ),
    turbo_pump = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = s7_io + 'turbo_pump',
        description = 'Turbo pump.',
        mapping = dict(off=0, on=1),
    ),
    pneu_actuator = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = s7_io + 'pneu_aktuator',
        description = 'Pneumatic actuator.',
        mapping = dict(off=0, on=1),
    ),
    vac_setpoint_1 = device('nicos.devices.entangle.DigitalInput',
        tangodevice = s7_io + 'vac_setpoint_1',
        description = 'Vacuum setpoint 1.',
    ),
    vac_setpoint_2 = device('nicos.devices.entangle.DigitalInput',
        tangodevice = s7_io + 'vac_setpoint_2',
        description = 'Vacuum setpoint 2.',
    ),
    vac_setpoint_3 = device('nicos.devices.entangle.DigitalInput',
        tangodevice = s7_io + 'vac_setpoint_3',
        description = 'vacuum Setpoint 3.',
    ),
)
