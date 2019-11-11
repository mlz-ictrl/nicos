description = 'Attocube sample translation units'

group = 'optional'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    xtrans_atto = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'attocube/motor1',
        description = 'X translation stage',
    ),
    xtrans_atto_ampl = device('nicos.devices.tango.AnalogOutput',
        tangodevice = tango_base + 'attocube/ampl1',
        description = 'X translation amplitude for the Piezo steps',
    ),
    ytrans_atto = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'attocube/motor2',
        description = 'Y translation stage',
    ),
    ytrans_atto_ampl = device('nicos.devices.tango.AnalogOutput',
        tangodevice = tango_base + 'attocube/ampl2',
        description = 'Y translation amplitude for the Piezo steps',
    ),
)
