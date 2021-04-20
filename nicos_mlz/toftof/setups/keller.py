description="setup for keller pressure sensor"

group="optional"

devices=dict(
    H2_pressure=device('nicos.devices.entangle.Sensor',
        description='Readout of a H2 keller sensor',
        tangodevice='tango://tofhw.toftof.frm2:10000/toftof/keller/sensor',
        unit='bar',
    ),
)
