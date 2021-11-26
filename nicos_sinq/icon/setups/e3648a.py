description = 'Setup for the control of the Agilent E3847A power supply'

devices = dict(
    e3648a_volt = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Voltage on Agilent E3648A',
        writepv = 'SQ:ICON:e3648a:VOLT',
        readpv = 'SQ:ICON:e3648a:VOLT_RBV',
        window = .1,
        abslimits = (0, 20)
    ),
    e3648a_curr = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Current on Agilent E3648A',
        writepv = 'SQ:ICON:e3648a:CURR',
        readpv = 'SQ:ICON:e3648a:CURR_RBV',
        window = .1,
        abslimits = (0, 5)
    ),
)
