description = 'Setup for the YMIR AreaDetector.'

pvprefix = '13SIM1'
detector_channel = 'cam1'
data_channel = 'image1'

devices = dict(
    ad=device(
        'nicos_ess.devices.epics.area_detector.EpicsAreaDetector',
        description='Area detector instance that can only interact with EPICS',
        statepv=f'{pvprefix}:{detector_channel}:DetectorState_RBV',
        startpv=f'{pvprefix}:{detector_channel}:Acquire',
        errormsgpv=f'{pvprefix}:{detector_channel}:StatusMessage_RBV',
        timers=['ad_acquire_time'],
        images=['ad_channel'],
    ),

    ad_channel=device(
        'nicos_ess.devices.epics.area_detector.ADImageChannel',
        description='The image channel',
        pvprefix=f'{pvprefix}:{detector_channel}',
        readpv=f'{pvprefix}:{data_channel}:ArrayData',
        lowlevel=True,
    ),

    ad_acquire_time=device(
        'nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description='Acquisition time preset',
        unit='s',
        fmtstr='%.3f',
        readpv=f'{pvprefix}:{detector_channel}:AcquireTime_RBV',
        presetpv=f'{pvprefix}:{detector_channel}:AcquireTime',
    ),

    time_remaining=device(
        'nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        description='Acquisition time remaining',
        unit='s',
        fmtstr='%.3f',
        readpv=f'{pvprefix}:{detector_channel}:TimeRemaining_RBV',
    ),

    ad_trigger_mode=device(
        'nicos_ess.devices.epics.extensions.EpicsMappedMoveable',
        description='Acquisition trigger mode',
        readpv=f'{pvprefix}:{detector_channel}:TriggerMode_RBV',
        writepv=f'{pvprefix}:{detector_channel}:TriggerMode',
        mapping={'Internal': 0,
                 'External': 1},
    ),
)
