description = '2 Beamstops 50x50mm one on the left, the other in Center'

group = 'lowlevel'

includes = ['vsd']

devices = dict(
    beamstop_height_foo = device('nicos_mlz.refsans.devices.beamstop.BeamStopDevice',
        description = 'height of both beamstops',
        unit = 'foo',
        att = 'User2Voltage',
        lowlevel = True,
    ),
    beamstop_height = device('nicos_mlz.refsans.devices.converters.LinearKorr',
        description = 'height of both beamstops',
        unit = 'mm',
        informula = '50 * x',
        dev = 'beamstop_height_foo',
    ),
    beamstop_asym = device('nicos_mlz.refsans.devices.beamstop.BeamStopDevice',
        description = 'Asymetric Beamstop in or out',
        unit = '',
        att = 'VSD_User2DigitalInput',
    ),
    beamstop_center = device('nicos_mlz.refsans.devices.beamstop.BeamStopCenter',
        description = 'center Beamstop in or out',
        unit = '',
        att = 'User2Current',
    ),
)
