description = 'Setup for the single detector at ZEBRA'

pvdet = 'SQ:ZEBRA:counter'

sysconfig = dict(datasinks = ['asciisink', 'cclsink'])

devices = dict(
    timepreset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvdet + '.TP',
        presetpv = pvdet + '.TP',
    ),
    elapsedtime = device('nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvdet + '.T',
    ),
    monitorpreset = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvdet + '.PR2',
        presetpv = pvdet + '.PR2',
    ),
    counts = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Actual counts',
        type = 'monitor',
        readpv = pvdet + '.S3',
    ),
    monitor1 = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'First scalar counter channel',
        type = 'monitor',
        readpv = pvdet + '.S2',
    ),
    protoncount = device('nicos_ess.devices.epics.detector'
        '.EpicsCounterPassiveChannel',
        description = 'Proton counter channel',
        type = 'monitor',
        readpv = pvdet + '.S5',
    ),
    intensity = device('nicos_sinq.sxtal.commands.Intensity',
        description = 'Dummy to try to get stuff to work'
    ),
    zebradet = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons',
        startpv = pvdet + '.CNT',
        pausepv = pvdet + ':Pause',
        statuspv = pvdet + ':Status',
        errormsgpv = pvdet + ':MsgTxt',
        thresholdpv = pvdet + '.PR4',
        thresholdcounterpv = pvdet + '.PR3',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = ['counts', 'monitor1', 'protoncount'],
        images = [],
        others = [],
        liveinterval = 7,
        saveintervals = [60]
    ),
    asciisink = device('nicos_sinq.sxtal.datasink.SxtalScanSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['zebra%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/zebra/zebra.hdd',
        visibility = (),
        scaninfo = [
            ('Counts', 'counts'), ('Monitor1', 'monitor1'),
            ('Time', 'elapsedtime')
        ]
    ),
    cclsink = device('nicos_sinq.sxtal.datasink.CCLSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['zebra%(year)sn%(scancounter)06d.ccl'],
        templatefile = 'nicos_sinq/zebra/mess.hdd',
        visibility = (),
        detector = 'counts',
        scaninfo = [
            ('Counts', 'counts'), ('Monitor1', 'monitor1'),
            ('Time', 'elapsedtime')
        ]
    ),
)
startupcode = """
SetDetectors(zebradet)
Exp._setROParam('forcescandata', False)
"""
