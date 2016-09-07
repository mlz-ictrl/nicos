description = 'sample changer sword'

group = 'plugplay'

includes = ['sample_changer']

tango_base = 'tango://ccmsanssc:10000/box/'

devices = dict(
    ccmsanssc_switch   = device('devices.tango.NamedDigitalOutput',
                                lowlevel = True,
                                tangodevice = tango_base + 'phytron/switch',
                                mapping = {'free': 1, 'closed': 2},
                               ),

    ccmsanssc_motor    = device('devices.tango.Motor',
                                lowlevel = True,
                                tangodevice = tango_base + 'phytron/motor',
                                abslimits = (0, 600),
                                unit = 'mm',
                               ),

    ccmsanssc_coder    = device('devices.tango.Sensor',
                                lowlevel = True,
                                tangodevice = tango_base + 'phytron/coder',
                                unit = 'mm',
                               ),

    ccmsanssc_axis     = device('sans1.ccmsanssc.SwordAxis',
                                description = 'translation of the sword',
                                abslimits = (0, 600),
                                motor = 'ccmsanssc_motor',
                                coder = 'ccmsanssc_coder',
                                obs = [],
                                startdelay = 1,
                                stopdelay = 1,
                                switch = 'ccmsanssc_switch',
                                switchvalues = (2, 1),
                                fmtstr = '%.2f',
                                precision = 0.1,
                                dragerror = 5,
                               ),

    ccmsanssc_position = device('devices.generic.Switcher',
                                description = 'position of the sample changer sword',
                                moveable = 'ccmsanssc_axis',
                                mapping = {1: 4, 2: 69, 3: 134, 4: 199, 5: 264,
                                           6: 329, 7: 394, 8: 459, 9: 524, 10: 589},
                                precision = 0.2,
                                fmtstr = '%d',
                               ),
)

alias_config = {
    'SampleChanger': {'ccmsanssc_position': 100},
}
