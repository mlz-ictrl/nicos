description = 'at samplecamper [slit k1]'

group = 'lowlevel'

tango_host = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/'

devices = dict(
    #
    ## smccorvusserver b2 exports
    #
    b2 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'b2 at sample pos',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        unit = '',
        slit_r = 'b2r',
        slit_s = 'b2s',
    ),
    b2r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, reactor side; 220 full access, 74 for upper srcews',
        motor = 'b2_r',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit':   0.0,
            'point':  -4.067,
            'gisans': 0.0, #  -218.645,
        },
        lowlevel = True,
        unit = 'mm',
    ),
    b2s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, sample side; -291 full access, -182 low row',
        motor = 'b2_s',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit':   0.0,
            'point':  -0.233,
            'gisans': -85, #  206.4,
        },
        unit = 'mm',
        lowlevel = True,
    ),
    b2_r = device('nicos.devices.generic.Axis',
        description = 'b2, reactorside',
        motor = 'smccorvus_b2mr',
        backlash = 0,
        precision = 0.02,
        unit = 'mm',
        lowlevel = True,
    ),
    b2_s = device('nicos.devices.generic.Axis',
        description = 'b2, sampleside',
        motor = 'smccorvus_b2ms',
        backlash = 0,
        precision = 0.02,
        unit = 'mm',
        lowlevel = True,
    ),
    smccorvus_b2mr = device('nicos.devices.tango.Motor',
        description = 'Device test/smccorvus/b2mr of Server smccorvusserver b2',
        tangodevice = tango_host + 'smccorvus/b2mr',
        abslimits = (-1294, 1222),
        lowlevel = True,
    ),
    smccorvus_b2ms = device('nicos.devices.tango.Motor',
        description = 'Device test/smccorvus/b2ms of Server smccorvusserver b2',
        tangodevice = tango_host + 'smccorvus/b2ms',
        abslimits = (-2960, 2130),
        lowlevel = True,
    ),
)

alias_config = {
    'last_aperture': {'b2.height': 100},
}
