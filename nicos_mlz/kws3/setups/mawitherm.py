description = 'Mawitherm temperature readout'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_mawi_1 = device('nicos.devices.tango.Sensor',
        description = 'temperature of channel 1',
        tangodevice = tango_base + 'mawitherm/ch1',
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    T_mawi_mean = device('nicos_mlz.kws3.devices.mawi.MeanTemp',
        description = 'mean temperature of some sensors',
        tangodevice = tango_base + 'mawitherm/all',
        first = 1,
        last = 8,
        unit = 'degC',
        fmtstr = '%.2f',
    ),
)

alias_config = {
    'Ts': {'T_mawi_1': 100, 'T_mawi_mean': 90},
}
