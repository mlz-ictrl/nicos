description = 'Setup for the CAMEA detector'

group = 'basic'

display_order = 50

sysconfig = dict(
    datasinks = ['nxsink'],
)

includes = ['mono_slit', 'cameabasic', 'hm_config'] # The real thing
#includes=['mono_slit', 'cameabasic', 'hm_config_sim'] # For simulation
excludes = ['andorccd']

pvprefix = 'SQ:CAMEA:counter'

devices = dict(
    nxsink = device('nicos.nexus.NexusSink',
        description = 'Sink for NeXus file writer',
        filenametemplate = ['camea%(year)sn%(scancounter)06d.hdf'],
        templateclass = 'nicos_sinq.camea.nexus.nexus_templates'
        '.CameaTemplateProvider',
    ),
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvprefix + '.TP',
        presetpv = pvprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvprefix + '.PR2',
        presetpv = pvprefix + '.PR2',
    ),
    monitor1 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'First scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S2',
    ),
    monitor2 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Second scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S3',
    ),
    monitor3 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'monitor',
        visibility = (),
        readpv = pvprefix + '.S4',
    ),
    monitor4 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Fourth scalar counter channel',
        type = 'monitor',
        visibility = (),
        readpv = pvprefix + '.S5',
    ),
    protoncount = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Fifth scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S6',
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    camea_detector = device('nicos_sinq.devices.sinqhm.channel.ReshapeHistogramImageChannel',
        description = "Image channel for area detector",
        visibility = (),
        bank = 'hm_bank0',
        dimensions = {
            'x': 1024,
            'y': 104
        },
        connector = 'hm_connector',
    ),
    counts = device('nicos.devices.generic.detector.RectROIChannel',
        description = 'Counts as ROI on camea detector',
        roi = (1, 2, 50, 60)
    ),
    cameadet = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        thresholdpv = pvprefix + ':Threshold',
        thresholdcounterpv = pvprefix + ':ThresholdCounter',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = [
            'monitor1', 'monitor2', 'monitor3', 'protoncount', 'monitor4'
        ],
        images = ['camea_detector'],
        counters = [
            'counts',
        ],
        postprocess = [
            ('counts', 'camea_detector'),
        ],
        others = ['histogrammer'],
        liveinterval = 20,
        saveintervals = [900]
    ),
    cter1 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Direct connection to counter box',
        commandpv = 'SQ:CAMEA:cter1' + '.AOUT',
        replypv = 'SQ:CAMEA:cter1' + '.AINP',
    ),
)
startupcode = """
SetDetectors(cameadet)
cter1.execute('DR 2')
cter1.execute('DL 2 100')
"""
