description = 'beam stop setup for detection stage'

group = 'lowlevel'
tango_base = 'tango://tango:8001/v6/beamstop_d/'

devices = dict(
    beam_d=device('nicos.devices.entangle.Motor',
                  description='Beam stop for detection stage',
                  tangodevice=tango_base + 'stop',
                  unit='deg',
                  ),
)
