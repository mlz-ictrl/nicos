description = 'Installs the Eulerian cradle into NICOS'

includes = ['morpheus', 'monochromator']

excludes = ['tas']

devices = dict(
    mess = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for measurements',
        reflection_list = []
    ),
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
        reflists = ['ublist', 'mess'],
        reflist = 'ublist',
    ),
    MORPHEUS = device('nicos_sinq.sxtal.instrument.EulerSXTal',
        description = 'instrument object',
        instrument = 'SINQ MORPHEUS',
        responsible = 'Jochen Stahn <jochen.stahn@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/morpheus/',
        ttheta = 'stt',
        omega = 'sth',
        chi = 'scx',
        phi = 'scy',
        mono = 'wavelength',
        center_counter = 'ctr1',
        center_steps = [.1, .1, .2, .2]
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'MORPHEUS.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'MORPHEUS.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'MORPHEUS.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    om = device('nicos.core.device.DeviceAlias',
        description = 'Alias for omega',
        alias = 'sth',
        devclass = 'nicos.core.device.Moveable'
    ),
    chi = device('nicos.core.device.DeviceAlias',
        description = 'Alias for chi',
        alias = 'scx',
        devclass = 'nicos.core.device.Moveable'
    ),
    phi = device('nicos.core.device.DeviceAlias',
        description = 'Alias for phi',
        alias = 'scy',
        devclass = 'nicos.core.device.Moveable'
    ),
)
