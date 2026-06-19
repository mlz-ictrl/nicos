description = 'Testing setup for microequipment dewpoint generator'

group = 'optional'

tango_base = 'tango://phys.jcnsse.frm2.tum.de:10000/jcnsse/dewpoint/'

devices = {
    f'T_{setupname}_dp': device('nicos.devices.entangle.Actuator',
        description = 'Dewpoint',
        tangodevice = tango_base + 'dewpoint',
        fmtstr = '%.2f',
    ),
    f'{setupname}_flow': device('nicos.devices.entangle.Actuator',
        description = 'Gas flow',
        tangodevice = tango_base + 'gasflow',
        fmtstr = '%.2f',
    ),
    f'{setupname}_ratio': device('nicos.devices.entangle.Actuator',
        description = 'H2O/D2O ratio',
        tangodevice = tango_base + 'ratio',
        fmtstr = '%.2f',
    ),
    f'{setupname}_mode': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Operation mode',
        tangodevice = tango_base + 'mode',
    ),
}
