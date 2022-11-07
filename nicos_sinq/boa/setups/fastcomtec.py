description = 'Setup for the FastcomTec MCA coming with the mobile ' \
              'chopper unit'

excludes = ['andor', 'embl']

counterprefix = 'SQ:BOA:counter'

devices = dict(
    el737_preset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = counterprefix + '.TP',
        presetpv = counterprefix + '.TP',
    ),
    elapsedtime = device('nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = counterprefix + '.T',
    ),
    monitorpreset = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = counterprefix + '.PR2',
        presetpv = counterprefix + '.PR2',
    ),
    monitorval = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for neutron beam',
        type = 'monitor',
        readpv = counterprefix + '.S2',
    ),
    protoncurr = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = counterprefix + '.S4',
    ),
    fastcomtec = device('nicos_sinq.boa.devices.fastcomtec.FastComtecChannel',
        description = 'FastComtec MCA channel',
        pvprefix = 'SQ:BOA:mca',
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = counterprefix + '.CNT',
        pausepv = counterprefix + ':Pause',
        statuspv = counterprefix + ':Status',
        errormsgpv = counterprefix + ':MsgTxt',
        monitorpreset = [
            'monitorpreset',
        ],
        timepreset = ['el737_preset'],
        thresholdpv = counterprefix + ':Threshold',
        thresholdcounterpv = counterprefix + ':ThresholdCounter',
    ),
    fcdet = device('nicos.devices.generic.detector.Detector',
        description = 'Dummy detector to encapsulate fastcomtec',
        monitors = [
            'fastcomtec',
        ],
        timers = [
            'fastcomtec',
        ],
        images = [
            'fastcomtec',
        ],
        visibility = ()
    ),
    boadet = device('nicos_sinq.devices.detector.ControlDetector',
        description = 'Fastcomtec detector coordination',
        trigger = 'el737',
        followers = ['fcdet'],
    )
)

startupcode = '''
SetDetectors(boadet)
'''
