description = 'High voltage via moxa box'
servername = 'EXV20'
nameservice = '192.168.1.254'

devices = dict(
    hv_mon = device('nicos.devices.vendor.caress.Driveable',
                    description = 'High voltage for beam monitor',
                    fmtstr = '%.2f',
                    unit = 'V',
                    abslimits = (0, 1400),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'HVMON 76 2 usemoxa 1 1 0 20 -1 0 0 0',
                   ),
)
