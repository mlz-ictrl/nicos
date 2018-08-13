description = 'Neutron counter box and channels in the SINQ AMOR.'

includes = ['hm_config', 'distances']

pvprefix = 'SQ:AMOR:counter'

devices = dict(
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
    c1=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='First scalar counter channel',
        type='monitor',
        lowlevel=True,
        readpv=pvprefix + '.S2',
    ),
    c2=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Second scalar counter channel',
        type='monitor',
        lowlevel=True,
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
    c4=device(
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
    area_detector=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description="Image channel for area detector",
        lowlevel=True,
        bank='hm_bank0',
        connector='hm_connector',
    ),
    single_det1=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 1",
        lowlevel=True,
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=0,
    ),
    single_det2=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 2",
        lowlevel=True,
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=1,
    ),
    psd_tof=device(
        'nicos_sinq.amor.devices.detector.AmorDetector',
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
        monitors=['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'],
        images=['area_detector', 'single_det1', 'single_det2'],
        others=['histogrammer'],
        liveinterval=30,
        saveintervals=[60]
    ),
    dist_chopper_detector=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of detector to chopper',
        distcomponent='ddetector',
        distreference='dchopper'
    ),
    dist_sample_detector=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of detector to sample',
        distcomponent='ddetector',
        distreference='dsample'
    )
)

startupcode = '''
SetDetectors(psd_tof)
'''
