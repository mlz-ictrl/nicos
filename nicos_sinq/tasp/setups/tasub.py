description = 'This initializes TASP for the UB matrix triple axis calculation'

sysconfig = dict(instrument = 'TASP',)

requires = ['tasp']

excludes = ['tasmlz']

modules = ['nicos_sinq.sxtal.commands']

devices = dict(
    ublist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'UB matrix refinement',
        reflection_list = []
    ),
    Sample = device('nicos_sinq.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
        ubmatrix = [
            -0.0550909, 0.04027, -0.075288, 0.0335794, 0.0925995, 0.0249626,
            0.0785034, -0.0113463, -0.0635126
        ],
        a = 9.8412,
        reflists = ['ublist'],
        reflist = 'ublist',
    ),
    TASP = device('nicos_sinq.sxtal.instrument.TASSXTal',
        description = 'instrument object',
        instrument = 'SINQ TASP',
        responsible = 'Alexandra Turrini <alexandra.turrini@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/tasp/',
        a3 = 'a3',
        a4 = 'a4',
        sgu = 'sgu',
        sgl = 'sgl',
        mono = 'mono',
        ana = 'ana',
        inelastic = True,
        out_of_plane = True,
        plane_normal = [0.015167, 0.005586, 0.999869],
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'TASP.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'TASP.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'TASP.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the en of hkle',
        alias = 'TASP.en',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
)
