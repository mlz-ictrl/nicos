description = 'B3 aperture devices'

# group = 'lowlevel'
group = 'optional'

uribase = 'tango://refsansctrl01.refsans.frm2:10000/refsans/b3/'

devices = dict(
    b3_m1 = device('devices.tango.Actuator',
                   tangodevice = uribase + '_blende_b3_m1',
                   lowlevel = True,
                  ),
    b3_m2 = device('devices.tango.Actuator',
                   tangodevice = uribase + '_blende_b3_m2',
                   lowlevel = True,
                  ),
    b3_m3 = device('devices.tango.Actuator',
                   tangodevice = uribase + '_blende_b3_m3',
                   lowlevel = True,
                  ),
    b3_m4 = device('devices.tango.Actuator',
                   tangodevice = uribase + '_blende_b3_m4',
                   lowlevel = True,
                  ),
    b3 = device('devices.generic.Slit',
                description = 'B3 aperture',
                top = 'b3_m4',
                bottom = 'b3_m3',
                left = 'b3_m1',
                right = 'b3_m2',
                coordinates = 'opposite',
                opmode = '4blades',
               ),
)
