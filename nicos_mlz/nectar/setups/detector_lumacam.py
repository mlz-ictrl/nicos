description = 'Timepix3 Detector at ILL'

group = 'optional'

sysconfig = dict(
    datasinks = ['LumaSink'],
)

base_pv = 'nectar:roadrunner:'
cam_base_pv = base_pv + 'tpx3cam:cam:'
empir_base_pv = base_pv + 'empir:'

# PLAN:
# detector:count()
    # - timer -> trigger -> acquire
    # - image?? would be nice
    # - FileSink:
        # - point count -> Filename
            # - lumasink_prepare_status waits for actual change in filename (need to do that for folder name as well?)
        # - folder name -> RawFilePath (does this work with sample names etc? 256 max chars?)
    # - status -> DetectorState_RBV
    # - lumasink_prepare_status as well
#
# Implement for tpx3:
#   - Config parameters
#   - prepare detector at init
#   - prepare detector before acquisition
#
# Implement for data reduction:
#   - all parameters
#   - communicate raw data folder to data reduction

    # # Acquisition parameters for tpx3/Serval
    # # Setting files are on the PC with serval
    # # Set Path to Bad Pixel Mask && load it
    # 'BPCFilePath'
    # 'BPCFileName'
    # 'WriteBPCFile'
    # # Set Path to DA Converter settings (sets voltage thresholds for pixels etc.) && load it
    # 'DACSFilePath'
    # 'DACSFileName'
    # 'WriteDACS'

    # plus settings in tpx3Spider_parameters.py (alex git repo)


devices = dict(

    PointCounter = device('nicos.devices.generic.manual.ManualMove',
        description = 'Share the current scan point count between devices.',
        abslimits = (0,9999999999),
        fmtstr = '%.0f',
        unit = '',
    ),

    # Workaround to get the folder and point count info to the detector
    LumaSinkPrepareStatus = device('nicos_mlz.nectar.devices.lumacam.LumaCamFileSinkStatus'),

    LumaSink = device('nicos_mlz.nectar.devices.lumacam.LumaCamSink',
        filenametemplate = ['%(pointcounter)08d'],
        filemode = 0o440,
        pointcounterout = 'PointCounter',
        status_prepare = 'LumaSinkPrepareStatus',
        foldernameout = 'FolderName',
        visibility = {'metadata', 'namespace', 'devlist'},
    ),

    FolderName = device('nicos_mlz.nectar.devices.lumacam.ManualStringMoveable',
        description = 'Foldername for the evaluated data.',
        unit = '',
    ),

    Trigger = device('nicos.devices.epics.pyepics.EpicsDigitalMoveable',
        readpv = base_pv + 'Acquire_RBV',
        writepv = base_pv + 'Acquire',
        fmtstr = '%.0f'
    ),

    Status = device('nicos_mlz.nectar.devices.lumacam.LumaCamStatus',
        readpv = base_pv + 'DetectorState_RBV',
    ),

    Timer = device('nicos_mlz.nectar.devices.lumacam.LumaCamTrigger',
        description = 'Software timer',
        runvalue = 1,
        stopvalue = 0,
        trigger_luma = 'Trigger',
        status_luma = 'Status',
    ),

    BiasVoltage = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'BiasVoltage_RBV',
        unit = 'V',
        # visibility = {'metadata', 'namespace'},
    ),
    AcquireBusy = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'AcquireBusy',
        # unit = 'V',
        # visibility = {'metadata', 'namespace'},
    ),

    HitRate = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'PelEvtRate_RBV',
        unit = 'Hit/s',
        fmtstr = '%.0f',
    ),
    ElapsedTime = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'ElapsedTime_RBV',
        unit = 's',
        fmtstr = '%.3f',
    ),
    StartTime = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'StartTime_RBV',
        unit = '',
        fmtstr = '%.0f',
    ),
    ImagesComplete = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'NumImagesCounter_RBV',
        unit = '',
        fmtstr = '%.0f',
    ),

    ChipTemperature = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'ChipTemps_RBV',
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    FreeDiskSpace = device('nicos.devices.epics.pyepics.EpicsReadable',
        readpv = base_pv + 'FreeSpace_RBV',
        unit = 'B',
        fmtstr = '%.0f',
    ),


    # TODO OPTIMIZE ACQUISITION TIME! TAKES FOREVER TO START\a

    DummyImage = device('nicos_mlz.nectar.devices.lumacam.DummyImageChannel',
        description = 'just to get the metadata',
    ),

    # Settings = device('nicos_mlz.antares.devices.lumacam.LumaCamSettingSwitcher',
    #     description = '',
    #     empir = 'Empir',
    #     lumacam = 'DetLumaCam',
    # ),

    DetLumaCam = device('nicos_mlz.nectar.devices.lumacam.ADLumaCam',
        # statepv = base_pv + 'DetectorState_RBV',
        # basepv = base_pv,
        # startpv = base_pv + 'Acquire',
        pvprefix = cam_base_pv[:-1],
        timers = ['Timer'],
        images = ['DummyImage'],
        status = 'Status',
        pointcounter = 'PointCounter',
        prepare_status = 'LumaSinkPrepareStatus',
        base_raw_file_path = 'file:/data/ILL_MOTO_2025-09-24',
        empir_path_prefix = 'file:/data/',
        # bad_pixel_config = '/home/localadmin/Programs/TPX3CAM/Settings/Settings_Timepix_2-3-001-0004_2024-12-12_Bias40/settings.bpc',
        # dac_config = '/home/localadmin/Programs/TPX3CAM/Settings/Settings_Timepix_2-3-001-0004_2024-12-12_Bias40/settings.bpc.dacs',
        empir_path_to_add = 'PathToAdd',
        # tpx3loglevel = 1,
        # tpx3biasvoltage = 40,
        # tpx3biasenabled = True,
        # tpx3polarity = 'Positive',
        # tpx3periphclk80 = True,
        # tpx3triggerin = 0,
        # tpx3triggerout = 0,
        # tpx3triggerperiod = 2.0,
        # tpx3exposuretime = 2.0,
        # tpx3triggerdelay = 0.0,
        # tpx3globaltimestampinterval = 0.1,
        # tpx3tdc0 = 'P0',
        # tpx3tdc1 = 'P0',
        # tpx3triggermode = 'Continuous',
        # tpx3rawsplitstg = 'frame',
        # tpx3numimages = 999999999,
        # tpx3rawfiletemplate = "%yyyy-MM-dd'T'HHmmss_",
        # empir_path_prefix = 'file:/data/',
    ),
    Empir = device('nicos_mlz.nectar.devices.lumacam.Empir',
        description = '',
        pvprefix = base_pv[:-1],
        px2ph_dspace = 2.0,
        px2ph_dtime = 5e-8,
        px2ph_npxmin = 2,
        ph2ev_dspace = 0.0,
        ph2ev_dtime = 0.0,
        ph2ev_durmax = 0.0,
        ph2ev_alg = '',
        evfilt_phmin = 1,
        evfilt_psdmin = 0.0,
        ev2img_sizex = 1024,
        ev2img_sizey = 1024,
        ev2img_texttrig = 'ignore',
        ev2img_tres = '',
        ev2img_tlim = '',
    ),
    PathToAdd = device('nicos.devices.epics.pyepics.EpicsStringMoveable',
        description = '',
        readpv = base_pv + 'path_toAdd',
        writepv = base_pv + 'path_toAdd',
    ),
)
startupcode = """
SetDetectors(DetLumaCam)
"""
