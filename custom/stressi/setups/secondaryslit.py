description = 'Secondary slit CARESS HWB xDevices'

group = 'optional'


servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    sst = device('devices.vendor.caress.Motor',
                 description = 'HWB SST',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = 0,
                 abslimits = (-15, 15),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'SST 115 11 0x00f1f000 4 100 200 20 1 0 0 0 0 1 3000'
                          ' 1 10 0 0 0',
                ),
     ssw = device('devices.generic.Axis',
                  description = 'Secondary Slit Width',
                  motor = device('devices.tango.Motor',
                      tangodevice = 'tango://stressictrl.stressi.frm2:10000/stressi/schunk/motor',
                      fmtstr = '%.1f',
                      unit = 'mm',
                      abslimits = (0, 60),
                      userlimits = (0, 20),
                      # requires =  {'level': 'admin',},
                     ),
                     precision = 0.01,
                ),
)
