description = 'Beckhoff bus coupler DAC channels.'
servername = 'EXV20'
nameservice = '192.168.1.254'

devices = dict(
      dac12b1_0 = device('devices.vendor.caress.Driveable',
                    description = 'DAC Channel 12B1_0',
                    requires={'level': 'user'},
                    fmtstr = '%.2f',
                    unit = 'V',
                    abslimits = (0,10),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'DAC12B1_0 82 5 192.168.1.2 0 2 2 3276.7 0',
                   ),
      dac12b2_0 = device('devices.vendor.caress.Driveable',
                    description = 'DAC Channel 12B2_0',
                    requires={'level': 'user'},
                    fmtstr = '%.2f',
                    unit = 'V',
                    abslimits = (-10,10),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'DAC12B2_0 82 5 192.168.1.2 0 34 2 3276.7 0',
                   ),
)
