description = 'collimator setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    L=device('nicos.devices.generic.ManualMove',
             description='distance',
             abslimits=(10000, 17000),
             unit='mm',
             default=10000,
             fmtstr='%d',
             requires={'level': 'admin'},
             ),
    pinhole=device('nicos.devices.entangle.NamedDigitalOutput',
                   description='hole diameter',
                   tangodevice=tango_base + 'collimator/motor',
                   requires={'level': 'admin'},
                   unit='mm',
                   ),
    collimator=device('nicos_lahn.astor.devices.collimator.CollimatorLoverD',
                      description='collimator ratio (L/D)',
                      l='L',
                      d='pinhole',
                      unit='L/D',
                      fmtstr='%.1f (v) x %.1f (h)',
                      ),
)
