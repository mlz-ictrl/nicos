description = 'Movement of T-spec device'

tango_base = configdata('localconfig.tango_base') + 'movement/'
dp_conf = configdata('localconfig.DP_CONF')
cp_conf = configdata('localconfig.CP_CONF')


devices = dict(
    cp = device('nicos.devices.entangle.Motor',
                description = cp_conf['description'],
                tangodevice = tango_base + 'cp/cp',
                precision = cp_conf['precision'],
                lowlevel = cp_conf['lowlevel'],
                abslimits = cp_conf['abslimits'],
                speed = cp_conf['speed'],
                unit = cp_conf['unit'],
                ),

    dp = device('nicos.devices.entangle.Motor',
                description = cp_conf['description'],
                tangodevice = tango_base + 'cp/cp',
                precision = cp_conf['precision'],
                lowlevel = cp_conf['lowlevel'],
                abslimits = cp_conf['abslimits'],
                speed = cp_conf['speed'],
                unit = cp_conf['unit'],
                ),
)
