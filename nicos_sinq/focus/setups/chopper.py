description = 'Setup for the FOCUS chopper'

pref = 'SQ:FOCUS:CH'

excludes = ['chopper_manual',]

devices = dict(
    ch1_speed = device('nicos_sinq.focus.devices.chopper.ChopperMoveable',
        description = 'Master chopper speed',
        precision = 10.,
        readpv = pref + '1:ASPEE_RBV',
        targetpv = pref + '1:NSPEE_RBV',
        writepv = pref + '1:Speed',
        unit = 'rpm',
        abslimits = (0, 20000)
    ),
    ch1vacuum = device('nicos_sinq.focus.devices.epics_devices.EpicsReadable',
        description = 'Chopper 1 Vaccum',
        readpv = pref + '1:VAKUUM_RBV'
    ),
    ch2_speed = device('nicos_sinq.focus.devices.chopper.ChopperMoveable',
        description = 'Slave chopper speed',
        precision = 10.,
        readpv = pref + '2:ASPEE_RBV',
        targetpv = pref + '2:NSPEE_RBV',
        writepv = pref + '2:Speed',
        unit = 'rpm',
        abslimits = (0, 20000)
    ),
    ch2vacuum = device('nicos_sinq.focus.devices.epics_devices.EpicsReadable',
        description = 'Chopper 2 Vaccum',
        readpv = pref + '2:VAKUUM_RBV'
    ),
    ch_phase = device('nicos_sinq.focus.devices.chopper.ChopperPhase',
        description = 'Slave chopper phase offset',
        precision = 0.5,
        readpv = pref + '2:NPHAS_RBV',
        writepv = pref + '2:Phase',
        targetpv = pref + '2:NPHAS_RBV',
        dphas = pref + '2:DPHAS_RBV',
        unit = 'degree',
        abslimits = (0, 360.)
    ),
    ch_ratio = device('nicos_sinq.focus.devices.chopper.ChopperRatio',
        description = 'Ratio master/slave speed',
        readpv = pref + '2:RATIO_RBV',
        targetpv = pref + '2:RATIO_RBV',
        writepv = pref + '2:Ratio',
        unit = '',
        abslimits = (1, 4)
    ),
)
