description = 'Sample environment aliases for tensile rig control'

group = 'lowlevel'

devices = dict(
    tepos = device('nicos.devices.generic.DeviceAlias'),
    teload = device('nicos.devices.generic.DeviceAlias'),
    teext = device('nicos.devices.generic.DeviceAlias'),
)

extended = dict(
    representative = 'teload',
)

startupcode = """
AddEnvironment(tepos, teload, teext)
"""
