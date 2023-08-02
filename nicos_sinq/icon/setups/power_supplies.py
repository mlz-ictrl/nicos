description = 'Control of power supplies'

display_order = 90

excludes = [
    'e3648a',
]

devices = dict(
    e3648a_volt = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Voltage on Agilent E3648A',
        writepv = 'SQ:ICON:e3648a:VOLT',
        readpv = 'SQ:ICON:e3648a:VOLT_RBV',
        precision = .1,
        abslimits = (0, 20)
    ),
    e3648a_curr = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Current on Agilent E3648A',
        writepv = 'SQ:ICON:e3648a:CURR',
        readpv = 'SQ:ICON:e3648a:CURR_RBV',
        precision = .1,
        abslimits = (0, 5)
    ),
    e3648a_chan = device('nicos.devices.epics.pyepics.EpicsDigitalMoveable',
        description = 'Channel selection on Agilent E3648A',
        writepv = 'SQ:ICON:e3648a:CHAN',
        readpv = 'SQ:ICON:e3648a:CHAN_RBV',
    ),
    rnd320_volt = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Voltage on RND320',
        writepv = 'SQ:ICON:rnd320:VOLT',
        readpv = 'SQ:ICON:rnd320:VOLT_RBV',
        precision = .1,
        abslimits = (0, 24)
    ),
    rnd320_curr = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Current on RND320',
        writepv = 'SQ:ICON:rnd320:CURR',
        readpv = 'SQ:ICON:rnd320:CURR_RBV',
        precision = .1,
        abslimits = (0, 10)
    ),
)
