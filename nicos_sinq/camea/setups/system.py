description = 'system setup'

group = 'lowlevel'

display_order = 10

includes = ['cameabasic', 'mono_slit']

sysconfig = dict(
    cache = 'localhost',
    instrument = 'CAMEA',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'quiecksink', 'nxsink'],
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands',
    'nicos_sinq.commands.epicscommands',
    'nicos_sinq.camea.commands.camea',
    'nicos.commands.tas',
    'nicos_sinq.sxtal.commands',
]

devices = dict(
    CAMEA = device('nicos_sinq.sxtal.instrument.TASSXTal',
        description = 'instrument object',
        instrument = 'SINQ CAMEA',
        responsible = 'Christoph Niedermayer <Christoph.Niedermayer@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/camea/',
        ana = 'ana',
        a3 = 'a3',
        a4 = 'a4',
        sgl = 'sgl',
        sgu = 'sgu',
        emode = 'FKE',
        mono = 'mono',
        ccl_file = False,
        center_counter = 'counts',
        scattering_sense = -1,
        inelastic = True,
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'CAMEA.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'CAMEA.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'CAMEA.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the en of hkle',
        alias = 'CAMEA.en',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    ublist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'UB matrix refinement',
        reflection_list = [],
        column_headers = (
            ('H', 'K', 'L', 'EN'), ('A3', 'A4', 'SGU', 'SGL'), ('EI', 'EF')
        ),
    ),
    Sample = device('nicos_sinq.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
        reflists = [
            'ublist',
        ],
        ubmatrix = [1, 0, 0, 0, 1, 0, 0, 0, 1],
        reflist = 'ublist',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
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
)
