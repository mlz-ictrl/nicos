description = 'Neutron counter box and channels in the SINQ AMOR.'

includes = ['hm_config']

pvprefix = 'SQ:AMOR:counter'

devices = dict(
    timepreset=device(
        'nicos_sinq.devices.epics.extensions.EpicsTimerActiveChannel',
        epicstimeout=3.0,
        description='Used to set and view time preset',
        unit='sec',
        readpv=pvprefix + '.TP',
        presetpv=pvprefix + '.TP',
    ),
    elapsedtime=device(
        'nicos_sinq.devices.epics.extensions.EpicsTimerPassiveChannel',
        epicstimeout=3.0,
        description='Used to view elapsed time while counting',
        unit='sec',
        readpv=pvprefix + '.T',
    ),
    countpreset=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterActiveChannel',
        epicstimeout=3.0,
        description='Used to set and view count preset',
        type='counter',
        readpv=pvprefix + '.PR2',
        presetpv=pvprefix + '.PR2',
    ),
    c1=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='First scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S2',
    ),
    c2=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Second scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S3',
    ),
    c3=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Third scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S4',
    ),
    c4=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Fourth scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S5',
    ),
    c5=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Fifth scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S6',
    ),
    c6=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Sixth scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S7',
    ),
    c7=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Seventh scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S8',
    ),
    c8=device(
        'nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        epicstimeout=3.0,
        description='Eighth scalar counter channel',
        type='counter',
        lowlevel=True,
        readpv=pvprefix + '.S9',
    ),
    hm_channel=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description="Histogram Memory Channel",
        connector='hm_connector'
    ),
    area_detector_channel=device(
        'nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description="Image channel for area detector",
        lowlevel=True,
        bank='hm_bank0',
        connector='hm_connector',
        serverbyteorder='little',
        databyteorder='little',
        readbytes=True,
    ),
    single_det1_channel=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 1",
        lowlevel=True,
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=0,
        readbytes=True,
    ),
    single_det2_channel=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 2",
        lowlevel=True,
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=1,
        readbytes=True,
    ),
    single_det3_channel=device(
        'nicos_sinq.amor.devices.image_channel.AmorSingleDetectorImageChannel',
        description="Image channel for single detector 3",
        lowlevel=True,
        bank='hm_bank1',
        connector='hm_connector',
        detectorid=2,
        readbytes=True,
    ),
    psd_tof=device(
        'nicos_sinq.devices.epics.scaler_record.EpicsScalerRecord',
        epicstimeout=3.0,
        description='EL737 counter box that counts neutrons and '
                    'starts streaming events',
        startpv=pvprefix + '.CNT',
        pausepv=pvprefix + ':Pause',
        statuspv=pvprefix + ':Status',
        errormsgpv=pvprefix + ':MsgTxt',
        timers=['timepreset', 'elapsedtime'],
        counters=['countpreset', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7',
                  'c8'],
        images=['area_detector_channel', 'single_det1_channel',
                'single_det2_channel', 'single_det3_channel'],
        others=['hm_channel'],
        liveinterval=5,
        saveintervals=[10]
    ),
)

startupcode = '''
SetDetectors(psd_tof)
'''
