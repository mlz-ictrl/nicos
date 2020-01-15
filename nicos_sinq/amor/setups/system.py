description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='Amor',
    experiment='Exp',
    datasinks=['conssink', 'dmnsink', 'NexusDataSink', 'HistogramDataSink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.file_writing',
           'nicos_sinq.amor.commands', 'nicos_sinq.commands.sics']

includes = ['laser']

devices = dict(
    Amor=device('nicos.devices.instrument.Instrument',
                description='instrument object',
                instrument='SINQ AMOR',
                responsible='Jochen Stahn <jochen.stahn@psi.ch>',
                operators=['Paul-Scherrer-Institut (PSI)'],
                facility='SINQ, PSI',
                website='https://www.psi.ch/sinq/amor/amor'
                ),

    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    Exp=device('nicos_sinq.amor.devices.experiment.AmorExperiment',
               description='experiment object',
               dataroot='/home/amor/',
               sample='Sample'
               ),

    Space=device('nicos.devices.generic.FreeSpace',
                 description='The amount of free space for storing data',
                 path=None,
                 minfree=5,
                 ),

    Shutter=device('nicos_sinq.amor.devices.sps_switch.AmorShutter',
                   description='Shutter controlled by SPS',
                   epicstimeout=3.0,
                   readpv='SQ:AMOR:SPS1:DigitalInput',
                   commandpv='SQ:AMOR:SPS1:Push',
                   commandstr="S0000",
                   byte=4,
                   bit=0,
                   brokenbyte=4,
                   brokenbit=3,
                   mapping={'CLOSED': False, 'OPEN': True}),

    SpinFlipper=device('nicos_sinq.amor.devices.sps_switch.SpsSwitch',
                       description='Spin flipper RF controlled by SPS',
                       epicstimeout=3.0,
                       readpv='SQ:AMOR:SPS1:DigitalInput',
                       commandpv='SQ:AMOR:SPS1:Push',
                       commandstr="S0007",
                       byte=12,
                       bit=7,
                       mapping={'SPIN DOWN': False,
                                'SPIN UP': True}),

    KafkaForwarderCommand=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarderControl',
        description="Configures commands to forward-epics-to-kafka",
        cmdtopic=configdata('config.FORWARDER_CMD_TOPIC'),
        instpvtopic="AMOR_metadata",
        instpvschema='f142',
        brokers=configdata('config.KAFKA_BROKERS'),
    ),

    KafkaForwarder=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description="Monitors and controls forward-epics-to-kafka",
        statustopic=configdata('config.FORWARDER_STATUS_TOPIC'),
        brokers=configdata('config.KAFKA_BROKERS'),
        forwarder_control='KafkaForwarderCommand'
    ),

    conssink=device('nicos.devices.datasinks.ConsoleScanSink'),

    dmnsink=device('nicos.devices.datasinks.DaemonSink'),

    NexusDataSink=device(
        'nicos_sinq.devices.datasinks.SinqNexusFileSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=configdata('config.KAFKA_BROKERS'),
        filenametemplate=['amor%(year)sn%(pointcounter)06d.hdf'],
        cmdtopic=configdata('config.FILEWRITER_CMD_TOPIC'),
        status_provider='NexusFileWriter',
        templatesmodule='nicos_sinq.amor.nexus.nexus_templates',
        templatename='amor_default',
        useswmr=False
    ),

    HistogramDataSink=device(
        'nicos_sinq.amor.devices.datasinks.ImageKafkaWithLiveViewDataSink',
        brokers=configdata('config.KAFKA_BROKERS'),
        channeltostream={
            'area_detector': ('AMOR_areaDetector', 'area.tof'),
            'single_det1': ('AMOR_singleDetector1', 'single.tof'),
            'single_det2': ('AMOR_singleDetector2', 'single.tof'),
        },
    ),

    NexusFileWriter=device(
        'nicos_sinq.amor.devices.nexus_updater.AmorNexusUpdater',
        description="Status for nexus file writing",
        brokers=configdata('config.KAFKA_BROKERS'),
        statustopic=configdata('config.FILEWRITER_STATUS_TOPIC'),
        timeout=30,
        fileupdates={
            '/entry1/AMOR/control/monitor1': ('monitorval', 'i32', 'cts'),
            '/entry1/AMOR/control/monitor2': ('protoncurr', 'i32', 'cts'),
            '/entry1/AMOR/control/time': ('elapsedtime', 'f32', 'sec')
        },
        binpaths=['/entry1/AMOR/area_detector/x_detector',
                  '/entry1/AMOR/area_detector/y_detector',
                  '/entry1/AMOR/area_detector/time_binning',
                  '/entry1/AMOR/single_detector_1/time_binning',
                  '/entry1/AMOR/single_detector_2/time_binning']
    ),

    Distances = device(
        'nicos_sinq.amor.devices.component_handler.DistancesHandler',
        description='Device to handle distance calculation in AMOR',
        components={
            'polariser': (-232, 0),
            'slit2': (302, 0),
            'slit3': (-22, 0),
            'slit4': (306, 0),
            'sample': (-310, 0),
            'detector': (326, 0),
            'selene': (-726, 0),
            'analyser': (310, 0)
        },
        fixedcomponents={
            'chopper': 9906,
            'filter': 8609,
            'slit1': 9010,
        },
        order=['chopper', 'slit1', 'filter', 'polariser', 'slit2', 'selene',
               'slit3', 'sample', 'slit4', 'analyser', 'detector'],
        switch='laser_switch',
        positioner='laser_positioner',
        dimetix='dimetix'
    )
)
