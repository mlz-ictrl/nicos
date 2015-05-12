description = 'kappa goniometer'
group = 'lowlevel'

devices = dict(
   twotheta =  device('devices.taco.Motor',
                      description = 'two-theta angle',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/twotheta',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f'),

   omega =  device('devices.taco.Motor',
                      description = 'omega angle',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/omega',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f'),

   kappa =  device('devices.taco.Motor',
                      description = 'kappa angle',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/kappa',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f'),

   phi =  device('devices.taco.Motor',
                      description = 'phi angle',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/phi',
                      abslimits = (-360, 360),
                      fmtstr = '%.3f'),

   stx =  device('devices.taco.Motor',
                      description = 'sample x translation',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/samplex',
                      abslimits = (-25, 25),
                      fmtstr = '%.3f'),

   sty =  device('devices.taco.Motor',
                      description = 'sample y translation',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/sampley',
                      abslimits = (-25, 25),
                      fmtstr = '%.3f'),

   stz =  device('devices.taco.Motor',
                      description = 'sample z translation',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/samplez',
                      abslimits = (-1, 25),
                      fmtstr = '%.3f'),

   detz =  device('devices.taco.Motor',
                      description = 'detector position',
                      tacodevice = '//lauectrl.laue.frm2/laue/hubermc9300/detz',
                      abslimits = (100, 200),
                      fmtstr = '%.3f'),
   gonio = device('nicos.laue.kappagon.KappaGon',
                   description = 'Full goniometer',
                   ttheta = 'twotheta',
                   omega = 'omega',
                   kappa = 'kappa',
                   phi ='phi',
                   dx = 'detz',
                   unit = '',
                   fmtstr ='%r'),

)
