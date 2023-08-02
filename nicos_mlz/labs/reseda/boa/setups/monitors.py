description = 'BOA monitor and timer devices'

counterprefix = 'SQ:BOA:counter'

devices = dict(
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = counterprefix + '.TP',
        presetpv = counterprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = counterprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = counterprefix + '.PR2',
        presetpv = counterprefix + '.PR2',
    ),
    monitorval = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for neutron beam',
        type = 'monitor',
        readpv = counterprefix + '.S2',
    ),
    protoncurr = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = counterprefix + '.S5',
    ),
)
