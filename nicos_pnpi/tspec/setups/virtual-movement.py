description = 'Movement of T-spec device'

excludes = ['movement']

dp_conf = configdata('localconfig.DP_CONF')
cp_conf = configdata('localconfig.CP_CONF')


devices = dict(
    cp = device('nicos.devices.generic.VirtualMotor',
                description = cp_conf['description'],
                precision = cp_conf['precision'],
                lowlevel = cp_conf['lowlevel'],
                abslimits = cp_conf['abslimits'],
                speed = cp_conf['speed'],
                unit = cp_conf['unit'],
                ),

    dp = device('nicos.devices.generic.VirtualMotor',
                description = cp_conf['description'],
                precision = cp_conf['precision'],
                lowlevel = cp_conf['lowlevel'],
                abslimits = cp_conf['abslimits'],
                speed = cp_conf['speed'],
                unit = cp_conf['unit'],
                ),
)
