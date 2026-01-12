description = 'slit 1 setup'

group = 'lowlevel'
tango_base = 'tango://tango:8001/v6/slit1/'
excludes = ['slit1_2']

devices = dict(
    up1=device('nicos.devices.entangle.Motor',
               description='beam limiter top blade',
               tangodevice=tango_base + 'up',
               abslimits=(0, 76),
               unit='mm',
               visibility=(),
               ),
    do1=device('nicos.devices.entangle.Motor',
               description='beam limiter bottom blade',
               tangodevice=tango_base + 'down',
               abslimits=(-10, 76),
               unit='mm',
               visibility=(),
               ),
    le1=device('nicos.devices.entangle.Motor',
               description='beam limiter left blade',
               tangodevice=tango_base + 'left',
               unit='mm',
               visibility=(),
               ),
    ri1=device('nicos.devices.entangle.Motor',
               description='beam limiter right blade',
               tangodevice=tango_base + 'right',
               unit='mm',
               visibility=(),
               ),
    slit_1=device('nicos.devices.generic.slit.Slit',
                  description='Slit system 1',
                  left='le1',
                  right='ri1',
                  top='up1',
                  bottom='do1',
                  opmode='offcentered',
                  coordinates='opposite',
                  ),
)
