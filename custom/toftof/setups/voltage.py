
includes = ['system']

devices = dict(
    lvbus = device('nicos.toftof.toni.ModBus',
		tacodevice = 'toftof/rs232/ifpowersupply',
		lowlevel = True),
    lv1 = device('nicos.toftof.lvpower.LVPower',
		bus = 'lvbus',
		unit = '',
		addr = 242,
		),
)
