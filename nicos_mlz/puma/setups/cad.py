description = 'Combined multianalyzer axis setup'

group = 'optional'

includes = ['analyser']

devices = dict(
    cad = device('nicos_mlz.puma.devices.coupledaxis.PumaCoupledAxis',
        description = 'cad - combined axis for multianalyzer',
        tt = 'att',
        th = 'ath',
        fmtstr = '%.3f',
        unit = 'deg',
        precision = 1.,
    ),
)

startupcode = '''
resetlimits(att)
resetlimits(ath)
'''
