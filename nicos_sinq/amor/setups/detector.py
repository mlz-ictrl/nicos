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
    monitorval=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Monitor for nutron beam',
        type='monitor',
        readpv=pvprefix + '.S2',
    ),
    protoncurr=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Monitor for proton current',
        type='monitor',
        readpv=pvprefix + '.S5',
    ),
    histogrammer=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description="Histogram Memory Channel",
        connector='hm_connector'
    ),
    area_detector=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description="Image channel for area detector",
        bank='hm_bank0',
        connector='hm_connector',
    ),
    single_det1=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 1",
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=0,
    ),
    single_det2=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 2",
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
        monitors=['monitorval', 'protoncurr'],
        images=['area_detector', 'single_det1', 'single_det2'],
        others=['histogrammer'],
        liveinterval=20,
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
