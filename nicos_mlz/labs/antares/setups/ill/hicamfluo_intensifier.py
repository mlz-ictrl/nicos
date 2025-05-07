description = 'Lambert HiCAM Fluo Intensifier'
group = 'optional'

includes = []

tango_base = 'tango://antareslamcam.office.frm2.tum.de:10000/antares/hicamfluo/'

devices = dict(
    MCP_Voltage = device('nicos.devices.entangle.AnalogOutput',
        description = 'HV across MCP',
        tangodevice = tango_base + 'mcp_voltage',
        unit = 'V',
        fmtstr = '%.0f',
        abslimits = (450, 910),
    ),
    MCP_Current = device('nicos.devices.entangle.Sensor',
        description = 'Current across the HV of the MCP',
        tangodevice = tango_base + 'mcp_current',
        pollinterval = 0.5,
        unit = 'µA',
    ),
    EnableGate = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Enable intensifier gate',
        tangodevice = tango_base + 'enable_gate',
        mapping = dict(Enabled = 1, Disabled = 0),
    ),
    TempIntensifier = device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the intensifier',
        tangodevice = tango_base + 'intensifier_temp',
        unit = '°C',
    ),
    TempSet = device('nicos.devices.entangle.AnalogOutput',
        description = 'Set the target temperature of the intensifier',
        tangodevice = tango_base + 'target_temp',
        unit = '°C',
        fmtstr = '%.0f',
    ),
    TempHeatsink = device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the (water-cooled) heat sink of the intensifier',
        tangodevice = tango_base + 'heatsink_temp',
        unit = '°C',
    ),
    SyncMode = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Sync mode controlling the intensifier gate',
        tangodevice = tango_base + 'sync_mode',
        mapping = dict(
            Disabled = 0,
            SyncExposure = 1,
            FollowExposure = 2,
            SyncInRising = 3,
            FollowSyncIn = 4,
            SyncManTrig = 5,
            SyncInFalling = 6,
            FixedFreq = 7
        ),
    ),
)
