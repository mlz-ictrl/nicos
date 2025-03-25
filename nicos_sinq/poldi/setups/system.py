description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POLDI',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'nxsink', 'quiecksink'],
)

modules = ['nicos.commands.standard', 'nicos_sinq.commands.sics',
           'nicos_sinq.commands.hmcommands']

devices = dict(
    POLDI = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ POLDI',
        responsible = 'Florencia Malamud <florencia.malamud@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/poldi/',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
        forcescandata = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sink for forwarding live data to the GUI',
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile '
        'notifications'
    ),
    nxsink = device('nicos.nexus.nexussink.NexusSink',
        description = 'Sink for NeXus file writer',
        filenametemplate = ['poldi%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.poldi.nexus.nexus_templates.POLDITemplateProvider',
    ),
    phimun = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description='Unknown motor',
        motorpv='SQ:POLDI:turboPmac1:PHIMUN',
    ),
)
