description = 'Setup for project P20211282'

devices = dict(
    e3648a_volt = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Voltage on Agilent E3648A',
        writepv = 'SQ:BOA:e3648a:VOLT',
        readpv = 'SQ:BOA:e3648a:VOLT_RBV',
        precision = .1,
        abslimits = (0, 20)
    ),
    e3648a_curr = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Current on Agilent E3648A',
        writepv = 'SQ:BOA:e3648a:CURR',
        readpv = 'SQ:BOA:e3648a:CURR_RBV',
        precision = .1,
        abslimits = (0, 5)
    ),
    e3648a_chan = device('nicos.devices.epics.EpicsDigitalMoveable',
        description = 'Channel selection on Agilent E3648A',
        writepv = 'SQ:BOA:e3648a:CHAN',
        readpv = 'SQ:BOA:e3648a:CHAN_RBV',
    ),
    rnd_volt = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Voltage on RND320',
        writepv = 'SQ:BOA:rnd320:VOLT',
        readpv = 'SQ:BOA:rnd320:VOLT_RBV',
        precision = .1,
        abslimits = (0, 24)
    ),
    rnd_curr = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Current on RND320',
        writepv = 'SQ:BOA:rnd320:CURR',
        readpv = 'SQ:BOA:rnd320:CURR_RBV',
        precision = .1,
        abslimits = (0, 10)
    ),
)
