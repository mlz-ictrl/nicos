description = 'Combined multianalyzer axis setup'

group = 'lowlevel'

includes = ['analyzer']

devices = dict(
    cad = device('nicos_mlz.puma.devices.PumaCoupledAxis',
        description = 'cad - combined axis for multianalyzer',
        tt = 'att_cad',
        th = 'ath',
        fmtstr = '%.3f',
        unit = 'deg',
        precision = .1,
    ),
    att_cad = device('nicos.devices.generic.Axis',
        description = 'Scattering angle two-theta of analyser',
        motor = 'st_att',
        precision = 0.01,
        offset = 90.,
        # offset = 0.,
        jitter = 0.2,
        dragerror = 1,
        maxtries = 30,
	# lowlevel = True,
    ),
)

startupcode = '''
att.userlimits = (-117, 117)
ath.userlimits = (0, 60)
'''
