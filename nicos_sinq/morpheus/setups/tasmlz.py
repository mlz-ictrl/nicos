description = 'This setup is for using the MLZ triple axis calculations'

group = 'basic'

includes = ['morpheus', 'monochromator', 'a34_aliases', 'slits']

sysconfig = dict(instrument = 'MORPHEUS',)

modules = [
    'nicos.commands.tas',
]

devices = dict(
    MORPHEUS = device('nicos_sinq.devices.tassinq.SinqTAS',
        description = 'MORPHEUS in MLZ mode',
        instrument = 'MORPHEUS',
        responsible = 'Michel Kenzelmann <Michel.Kenzelmann@psi.ch>',
        cell = 'Sample',
        phi = 'stt',
        psi = 'sth',
        mono = 'wavelength',
        ana = 'wavelength',
        alpha = None,
        psi360 = False,
        scatteringsense = (-1, 1, -1),
        energytransferunit = 'meV',
        axiscoupling = False,
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Sample under investigation',
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'MORPHEUS.h',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'MORPHEUS.k',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'MORPHEUS.l',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the transferred energy',
        alias = 'MORPHEUS.E',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
)
# Why below is required for en but none of the others, I do not understand
startupcode = """
en.alias=MORPHEUS.E
wavelength.unit='meV'
"""
