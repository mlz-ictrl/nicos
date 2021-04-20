description = 'Funktionsgenerator HP33220'

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/hp33220a_1/'

devices = dict(
    #
    ## hp33250aserver wave1 exports
    #
    hp33220a_1_freq = device('nicos.devices.entangle.AnalogOutput',
        description = 'freq of wave1',
        tangodevice = tango_base + 'freq',
        abslimits = (0, 1e6),
    ),
    hp33220a_1_amp = device('nicos.devices.entangle.AnalogOutput',
        description = 'amp of wave1',
        tangodevice = tango_base + 'amp',
        abslimits = (0, 10),
    ),
)
