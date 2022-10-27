description = 'horizontal beam delimiter setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    slit_left=device('nicos.devices.entangle.Motor',
                     description='beam delimiter left blade',
                     tangodevice=tango_base + 'sw/left',
                     visibility=(),
                     ),
    slit_right=device('nicos.devices.entangle.Motor',
                      description='beam delimiter right blade',
                      tangodevice=tango_base + 'sw/right',
                      visibility=(),
                      ),
    sw=device('nicos.devices.generic.slit.HorizontalGap',
              description='slit width',
              left='slit_left',
              right='slit_right',
              coordinates='opposite',
              opmode='centered',
              fmtstr='%.2f',
              requires={'level': 'admin'},
              unit='mm',
              ),
)
