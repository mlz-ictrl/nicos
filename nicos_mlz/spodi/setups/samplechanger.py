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
            'S1': -3.04,
            'S2': 33.11,
            'S3': 68.8,
            'S4': 104.95,
            'S5': 140.93,
            'S6': 177.20,
            'S7': 212.91,
            'S8': 249.07,
            'S9': 285.11,
            'S10': 321.03,
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
