description = 'Installs the Triple Axis Calculations into MORPHEUS'

# WARNING 555: This is a test version for development

requires = ['morpheus', 'monochromator']

excludes = ['euler']

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
    om = device('nicos.core.device.DeviceAlias',
        description = 'Alias for omega',
        alias = 'sth',
        devclass = 'nicos.core.device.Moveable'
    ),
    MORPHEUS = device('nicos_sinq.sxtal.instrument.TASSXTal',
        description = 'instrument object',
        instrument = 'SINQ MORPHEUS',
        responsible = 'Jochen Stahn <jochen.stahn@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/morpheus/',
        a3 = 'sth',
        a4 = 'stt',
        sgu = 'sgx',
        sgl = 'sgy',
        mono = 'wavelength',
        ana = 'wavelength',
        inelastic = True,
        out_of_plane = True,
        plane_normal = [0.015167, 0.005586, 0.999869],
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
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the en of hkle',
        alias = 'MORPHEUS.en',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    sgu = device('nicos.core.device.DeviceAlias',
        description = 'Alias for omega',
        alias = 'sgx',
        devclass = 'nicos.core.device.Moveable'
    ),
    sgl = device('nicos.core.device.DeviceAlias',
        description = 'Alias for omega',
        alias = 'sgy',
        devclass = 'nicos.core.device.Moveable'
    ),
)
