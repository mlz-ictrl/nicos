description = 'Instrument shutter'

devices = dict(
    thermal_shutter=device(
        'nicos.devices.generic.manual.ManualSwitch',
        description="Shutter",
        states=["OPEN", "CLOSED"],
    ),
)
