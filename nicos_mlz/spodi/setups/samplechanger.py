description = 'Sample changer and rotation'

group = 'optional'

tangohost = 'tango://spodictrl.spodi.frm2.tum.de:10000/spodi/samplechanger/sc_'

devices = dict(
    samr = device('nicos.devices.tango.NamedDigitalOutput',
        description = '(de-)activates the sample rotation',
        tangodevice = tangohost + 'rotation',
        mapping = dict(on=1, off=0),
    ),
    sams_e = device('nicos.devices.tango.Sensor',
        description = 'Position of the sample change selection wheel',
        tangodevice = tangohost + 'selectencoder',
        unit = 'deg',
        lowlevel = True,
    ),
    sams_m = device('nicos.devices.tango.Actuator',
        description = 'Motor position of the sample change selection wheel',
        tangodevice = tangohost + 'selectmotor',
        unit = 'deg',
        lowlevel = True,
    ),
    sams_a = device('nicos.devices.generic.Axis',
        description = 'Position of sample selection wheel',
        motor = 'sams_m',
        coder = 'sams_e',
        precision = 0.05,
        lowlevel = True,
    ),
    sams = device('nicos.devices.generic.Switcher',
        description = 'Sample Changer drum',
        moveable = 'sams_a',
        mapping = {
            'S1': 1.50,
            'S2': 19.56,
            'S3': 37.68,
            'S4': 55.53,
            'S5': 73.67,
            'S6': 91.76,
            'S7': 109.71,
            'S8': 127.70,
            'S9': 145.68,
            'S10': 163.70,
        },
        fallback = '?',
        fmtstr = '%s',
        precision = 0.1,
        blockingmove = False,
        lowlevel = False,
        unit = '',
    ),
)
display_order = 60

alias_config = {
}
