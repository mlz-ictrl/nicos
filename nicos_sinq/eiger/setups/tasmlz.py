description = 'This setup is for using the MLZ triple axis calculations'

group = 'basic'

includes = ['eiger', 'monochromator']

sysconfig = dict(instrument = 'EIGER',)

modules = ['nicos.commands.tas']

devices = dict(
    EIGER = device('nicos_sinq.devices.tassinq.SinqTAS',
        description = 'EIGER in MLZ mode',
        instrument = 'SINQ EIGER',
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
        autodevice_visibility = {'devlist', 'namespace', 'metadata'},
    ),
)
