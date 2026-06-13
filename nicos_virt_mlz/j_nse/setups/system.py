description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'NSE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'amqpsink'],
)

modules = ['nicos.commands.standard']

devices = dict(
    NSE = device('nicos_mlz.j_nse.devices.instrument.JnseInstrument',
        description = 'instrument object',
        instrument = 'VJNSE',
        responsible = 'O. Holderer <o.holderer@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/j-nse',
        table_filename = 'nicos_mlz/j_nse/NIST_table.csv',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        # cannot use /data until main instrument control is switched to NICOS
        dataroot = 'data',
        sendmail = True,
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    amqpsink = device('nicos_mlz.devices.datasinks.rabbitmq.RabbitSink',
        rabbit_url = 'amqp://workbench:w0rkb3nc4@rabbitmq.rabbitmq-stage.svc.cluster.local:5672',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
