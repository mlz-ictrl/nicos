description = 'This setup is for using the MLZ triple axis calculations'

excludes = ['tasub']

includes = ['eiger']

sysconfig = dict(instrument = 'EIGER',)

modules = ['nicos.commands.tas']

devices = dict(
    EIGER = device('nicos_sinq.devices.tassinq.SinqTAS',
        description = 'EIGER in MLZ mode',
        instrument = 'EIGER',
        responsible = 'Uwe Stuhr <uwe.stuhr@psi.ch>',
        cell = 'Sample',
        phi = 'a4',
        psi = 'a3',
        mono = 'mono',
        ana = 'ana',
        alpha = None,
        psi360 = False,
        scatteringsense = (1, -1, 1),
        energytransferunit = 'meV',
        axiscoupling = False,
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'EIGER.h',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'EIGER.k',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'EIGER.l',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the transferred energy',
        alias = 'EIGER.E',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
)
# Why the code below is required for en but none of the others, I do not
# understand
startupcode = """
en.alias=EIGER.E
"""
