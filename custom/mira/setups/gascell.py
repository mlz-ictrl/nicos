description = 'alfonso pressure module'
group = 'optional'

devices = dict(
	diptron3plus = device('devices.tango.AnalogInput',
		tangodevice = 'tango://mira1.mira.frm2:10000/mira/alfonsomodule/diptron3',
		description = 'Pressure at Diptron 3 Plus',
		pollinterval = 0.7,
		maxage = 2,
		fmtstr = '%.3f',
		unit = 'bar',
	),
	sentronicplus = device('devices.tango.Actuator',
		tangodevice = 'tango://mira1.mira.frm2:10000/mira/alfonsomodule/sentronic',
		description = 'Sentronic PLUS digital proportioning valve',
		abslimits = (0, 25.0),
		warnlimits = (0, 10.0),
		pollinterval = 0.7,
		maxage = 2,
		fmtstr = '%.3f',
		unit = 'bar',
	),
)
