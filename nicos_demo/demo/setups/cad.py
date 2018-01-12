description = 'Combined multianalyzer axis setup'

group = 'optional'

includes = ['tas']

devices = dict(
    cad = device('nicos_mlz.puma.devices.coupledaxis.PumaCoupledAxis',
        description = 'cad - combined axis for multianalyzer',
        tt = 'att',
        th = 'ath',
        fmtstr = '%.3f',
        unit = 'deg',
        precision = .1,
    ),
)

startupcode = '''
att.userlimits = (-117, 117)
ath.userlimits = (0, 60)
'''
