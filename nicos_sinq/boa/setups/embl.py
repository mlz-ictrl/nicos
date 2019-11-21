description = 'Neutron counter box and HM at SINQ BO.'

group = 'lowlevel'

includes = ['embl_config']
excludes = ['single_el737',]

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
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    area_detector = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel for area detector",
        bank = 'hm_bank0',
        connector = 'hm_connector',
    ),
    embl_tof = device('nicos_sinq.devices.detector.SinqDetector',
        epicstimeout = 3.0,
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        thresholdpv = pvprefix + ':Threshold',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = ['monitorval', 'protoncurr'],
        images = [
            'area_detector',
        ],
        others = ['histogrammer'],
        liveinterval = 20,
        saveintervals = [60]
    ),
)

startupcode = '''
SetDetectors(embl_tof)
'''
