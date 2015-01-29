description = 'POLI sample table'

group = 'lowlevel'

includes = []

nethost = 'heidi22.poli.frm2'

devices = dict(
    omega = device('devices.taco.Axis',
                   description = 'table omega axis',
                   tacodevice = '//%s/heidi2/table/omega' % (nethost, ),
                   pollinterval = 15,
                   maxage = 61,
                   fmtstr = '%.2f',
                   abslimits = (-180, 180),
                  ),
    chi1 = device('devices.taco.Axis',
                  description = 'table chi1 axis',
                  tacodevice = '//%s/heidi2/table/chi1' % (nethost, ),
                  pollinterval = 15,
                  maxage = 61,
                  fmtstr = '%.2f',
                  abslimits = (-5, 5),
                 ),
    chi2 = device('devices.taco.Axis',
                  description = 'table chi2 axis',
                  tacodevice = '//%s/heidi2/table/chi2' % (nethost, ),
                  pollinterval = 15,
                  maxage = 61,
                  fmtstr = '%.2f',
                  abslimits = (-5, 5),
                 ),
    twotheta = device('devices.taco.Axis',
                      description = 'table 2theta axis',
                      tacodevice = '//%s/heidi2/table/2theta' % (nethost, ),
                      pollinterval = 15,
                      maxage = 61,
                      fmtstr = '%.2f',
                      abslimits = (-20, 130),
                     ),
    liftingctr = device('devices.taco.Axis',
                      description = 'lifting counter axis',
                      tacodevice = '//%s/heidi2/table/lftctr' % (nethost, ),
                      pollinterval = 15,
                      maxage = 61,
                      fmtstr = '%.2f',
                      abslimits = (-5, 30),
                     ),
)

startupcode = """
"""
