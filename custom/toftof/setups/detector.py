description = 'TOF counter device'

group = 'lowlevel'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    det = device('toftof.tofcounter.TofCounter',
                 description = 'The TOFTOF detector device',
                 tacodevice = '//%s/toftof/tof/tofhistcntr' % (nethost),
                 monitor = '//%s/toftof/tof/tofmoncntr' % (nethost),
                 timer = '//%s/toftof/tof/toftimer' % (nethost),
                 pollinterval = None,
                ),
)
