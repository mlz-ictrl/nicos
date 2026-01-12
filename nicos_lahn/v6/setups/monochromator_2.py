description = 'Monochromator setup'

group = 'lowlevel'
tango_base = 'tango://tango:8001/v6/monochromator/'
excludes = ['monochromator_1']

devices = dict(
    high_m=device('nicos.devices.entangle.Motor',
                  description='Vertical movement',
                  tangodevice=tango_base + 'high',
                  unit='mm',
                  ),
    lin_m=device('nicos.devices.entangle.Motor',
                 description='Horizontal movement',
                 tangodevice=tango_base + 'lin',
                 unit='mm',
                 ),
    phi_m=device('nicos.devices.entangle.Motor',
                 description='Tilt angle',
                 tangodevice=tango_base + 'phi',
                 unit='deg',
                 ),
    omega_m=device('nicos.devices.entangle.Motor',
                   description='Rocking angle',
                   tangodevice=tango_base + 'omega',
                   unit='deg',
                   ),
    wavelength=device('nicos.devices.tas.Monochromator',
                      description='monochromator wavelength',
                      unit='A',
                      material='PG',
                      reflection=(0, 0, 2),
                      dvalue=3.355,
                      theta='omega_m',
                      twotheta='lin_m',
                      focush=None,
                      focusv=None,
                      abslimits=(4.5668, 4.7532),
                      crystalside=1,
                      ),
)
