description = 'Neutron counter box'

group = 'lowlevel'

excludes = ['embl', 'embl_config']

pvprefix = 'SQ:BOA:counter'

devices = dict(
    timepreset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvprefix + '.TP',
        presetpv = pvprefix + '.TP',
    ),
    elapsedtime = device('nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        epicstimeout = 3.0,
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvprefix + '.T',
    ),
    monitorpreset = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvprefix + '.PR2',
        presetpv = pvprefix + '.PR2',
    ),
    monitorval = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Monitor for nutron beam',
        type = 'monitor',
        readpv = pvprefix + '.S2',
    ),
    protoncurr = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = pvprefix + '.S5',
    ),
    countval = device('nicos_ess.devices.epics.detector'
                  '.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Actual counts in single detector',
        type = 'monitor',
        readpv = pvprefix + '.S1',
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        epicstimeout = 3.0,
        description = 'EL737 counter box that counts neutrons and manages '
        'monitors',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        thresholdpv = pvprefix + ':Threshold',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = ['monitorval', 'protoncurr'],
        liveinterval = 20,
        saveintervals = [60]
    ),
)

startupcode = '''
SetDetectors(el737)
'''
