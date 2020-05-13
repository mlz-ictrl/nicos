description = "Instrument shutter"

devices = dict(
    fast_shutter=device("nicos.devices.generic.ManualSwitch",
        description="Shutter just before the sample",
        states=["Open", "Closed"],
    ),
    heavy_shutter=device("nicos.devices.generic.ManualSwitch",
        description="Main shutter",
        states=["Open", "Closed"],
    ),
)
