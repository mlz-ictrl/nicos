description = 'Safety detector system'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base']

URL = instrument_values['url_base'] % 'savedetector'

devices = dict(
    sds = device(code_base + 'gkssjson.SdsRatemeter',
        description = description,
        lowlevel = False,
        # valuekey = 'time',
        valuekey = 'mon_alarm',
        unit = 'cps',
        url = URL + 'json?1',
        controlurl = 'control.html',
        masks = {
            'reflectivity': 200,
            'gisans': 100,
        },
    ),
)
