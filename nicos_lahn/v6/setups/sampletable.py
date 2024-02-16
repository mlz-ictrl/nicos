description = 'sample table setup'

group = 'lowlevel'

nameservice = '172.16.1.1'
servername = 'NVMEV6'

devices = dict(
	chi = device('nicos.devices.vendor.caress.EKFMotor',
				 description = 'sample table rotation chi',
				 fmtstr = '%.2f',
				 unit = 'deg',
				 abslimits = (-2, 2),
				 nameserver = '%s' % nameservice,
				 objname = '%s' % servername,
				 config = 'CHI_S 115 11 0x00f1f000 4 168 512 32 1 0 0 0 0 1 '
						 '5000 10 50 0 0 0',
    ),
)
