description = 'POLI shutter devices'
group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

_MAP_SHUTTER = {
    'open': 1,
    'closed': 0,
}

devices = dict(
    Shutter = device('nicos_mlz.jcns.devices.shutter.Shutter',
        description = 'POLI shutter control',
        tangodevice = tango_base + 's7_io/shutter',
        mapping = _MAP_SHUTTER,
    ),
)
