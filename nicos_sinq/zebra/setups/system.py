description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'quiecksink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands', 'nicos_sinq.commands.epicscommands',
    'nicos_sinq.sxtal.commands'
]

devices = dict(
    ublist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'UB matrix refinement',
        reflection_list = []
    ),
    messlist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'measuring reflections',
        reflection_list = []
    ),
    satref = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'measuring satellit reflections',
        reflection_list = []
    ),
    Sample = device('nicos_sinq.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
        reflists = ['ublist', 'messlist', 'satref'],
        reflist = 'ublist',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    zebramode = device('nicos.devices.generic.ManualSwitch',
        description = 'Device holding the crystallographic operating mode',
        states = ['bi', 'nb', 'tas']
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile notifications'
    ),
)
