description = 'alfonso pressure module'
group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    diptron3plus  = device('devices.tango.AnalogInput',
                           tangodevice = tango_base + 'alfonsomodule/diptron3',
                           description = 'Pressure at Diptron 3 Plus',
                           pollinterval = 0.7,
                           maxage = 2,
                           fmtstr = '%.3f',
                           unit = 'bar',
                          ),
    sentronicplus = device('devices.tango.Actuator',
                           tangodevice = tango_base + 'alfonsomodule/sentronic',
                           description = 'Sentronic PLUS digital proportioning valve',
                           warnlimits = (0, 10.0),
                           pollinterval = 0.7,
                           maxage = 2,
                           fmtstr = '%.3f',
                           unit = 'bar',
                          ),
    kistler       = device('devices.tango.AnalogInput',
                           tangodevice = tango_base + 'alfonsomodule/kistler',
                           description = 'Kistler Charge Meter for Calibration with Piezo Sensor',
                           pollinterval = 0.7,
                           maxage = 2,
                           fmtstr = '%.3f',
                           unit = 'N',
                          ),
)
