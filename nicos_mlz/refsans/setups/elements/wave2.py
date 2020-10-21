description = 'Funktionsgenerator HP33220'

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/hp33220a_2/'

devices = dict(
    #
    ## hp33250aserver wave2 exports
    #
    hp33220a_2_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'freq of wave2',
        tangodevice = tango_base + 'freq',
        abslimits = (0, 1e6),
    ),
    hp33220a_2_amp = device('nicos.devices.tango.AnalogOutput',
        description = 'amp of wave2',
        tangodevice = tango_base + 'amp',
        abslimits = (0, 10),
    ),
)
