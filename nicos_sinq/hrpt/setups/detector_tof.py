description = 'Detector devices in SINQ HRPT.'

pvmprefix = 'SQ:HRPT:motc:'
pvprefix = 'SQ:HRPT:counter'

includes = ['hm_config_tof']
excludes = ['detector']

devices = dict(
    s2t=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Detector Two Theta',
               motorpv=pvmprefix + 'STT',
               errormsgpv=pvmprefix + 'STT-MsgTxt',
               precision=0.01,
                   ),
    timepreset=device(
        'nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        epicstimeout=3.0,
        description='Used to set and view time preset',
        unit='sec',
        readpv=pvprefix + '.TP',
        presetpv=pvprefix + '.TP',
    ),
    elapsedtime=device(
        'nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        epicstimeout=3.0,
        description='Used to view elapsed time while counting',
        unit='sec',
        readpv=pvprefix + '.T',
    ),
    monitorpreset=device(
        'nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        epicstimeout=3.0,
        description='Used to set and view monitor preset',
        type='monitor',
        readpv=pvprefix + '.PR2',
        presetpv=pvprefix + '.PR2',
    ),
    monitor1=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='First scalar counter channel',
        type='monitor',
        readpv=pvprefix + '.S2',
    ),
    monitor2=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Second scalar counter channel',
        type='monitor',
        readpv=pvprefix + '.S3',
    ),

    c3=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Third scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S4',
    ),
    protoncount=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Fourth scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S5',
    ),
    c5=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Fifth scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S6',
    ),
    c6=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Sixth scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S7',
    ),
    c7=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Seventh scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S8',
    ),
    c8=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Eighth scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S9',
    ),
    histogrammer=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description="Histogram Memory Channel",
        connector='hm_connector'
    ),
    linear_detector=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description="Image channel for area detector",
        lowlevel=True,
        bank='hm_bank0',
        connector='hm_connector',
    ),
    hrptdet=device(
        'nicos_sinq.devices.detector.SinqDetector',
        epicstimeout=3.0,
        description='EL737 counter box that counts neutrons and '
                    'starts streaming events',
        startpv=pvprefix + '.CNT',
        pausepv=pvprefix + ':Pause',
        statuspv=pvprefix + ':Status',
        errormsgpv=pvprefix + ':MsgTxt',
        thresholdpv=pvprefix + ':Threshold',
        monitorpreset='monitorpreset',
        timepreset='timepreset',
        timers=['elapsedtime'],
        monitors=['monitor1', 'monitor2', 'c3', 'protoncount','c5', 'c6', 'c7', 'c8'],
        images=['linear_detector'],
        others=['histogrammer'],
        liveinterval=7,
        saveintervals=[60]
    )
)
startupcode = """
SetDetectors(hrptdet)
"""
