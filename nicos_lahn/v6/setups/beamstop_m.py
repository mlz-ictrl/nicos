description = 'beam stop setup for monochromation stage'

group = 'lowlevel'
tango_base = 'tango://tango:8001/v6/beamstop_m/'

devices = dict(
    beam_m=device('nicos.devices.entangle.Motor',
                  description='Beam stop for monochromation stage',
                  tangodevice=tango_base + 'stop',
                  unit='deg',
                  ),
)
