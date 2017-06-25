description = 'TOF counter devices'

group = 'lowlevel'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    timer = device('toftof.tofcounter.Timer',
                   description = 'The TOFTOF timer',
                   tacodevice = '//%s/toftof/tof/toftimer' % (nethost),
                   fmtstr = '%.1f',
                   lowlevel = True,
                  ),
    monitor = device('toftof.tofcounter.Monitor',
                     description = 'The TOFTOF monitor',
                     tacodevice = '//%s/toftof/tof/tofmoncntr' % (nethost),
                     type = 'monitor',
                     fmtstr = '%d',
                     unit = 'cts',
                     lowlevel = True,
                    ),
    image = device('toftof.tofcounter.Image',
                   description = 'The TOFTOF image',
                   tacodevice = '//%s/toftof/tof/tofhistcntr' % (nethost),
                   fmtstr = '%d',
                   unit = 'cts',
                   lowlevel = True,
                  ),
    det = device('toftof.detector.Detector',
                 description = 'The TOFTOF detector device',
                 timers = ['timer'],
                 monitors = ['monitor'],
                 counters = [],
                 images = ['image'],
                 rc = 'rc_onoff',
                 chopper = 'ch',
                 chdelay = 'chdelay',
                 pollinterval = None,
                 liveinterval = 10.0,
                 saveintervals = [30.],
                 detinfofile = '/opt/nicos/custom/toftof/detinfo.dat',
                ),
)
