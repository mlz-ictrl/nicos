description = 'Chopper phase timing, readout for light barrier and coder index'

group = 'lowlevel'

window_delay = 120

all_lowlevel = False  # or True
dev_class = 'nicos_mlz.refsans.devices.gkssjson.CPTReadout'

instrument_values = configdata('instrument.values')

URL = (instrument_values['url_base'] % 'cpt') + 'json-visual'

devices = dict(
    cpt0 = device(dev_class,
        description = 'Disc 1 light barrier ' + description + ' Phase of Disk1!',
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = -1,
        offset = 0.0,
        unit = 'deg',
        lowlevel = True,
    ),
    cpt1 = device(dev_class,
        description = 'Disc 1 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 0,
        # offset = 0,
        unit = 'rpm',
    ),
    cpt2 = device(dev_class,
         description = 'Disc 2 light barrier ' + description,
         url = URL,
         valuekey = 'chopper_act',
         timeout = 3.0,
         channel = 7,
         offset = 28.44 + window_delay,
         unit = 'deg',
     ),
    cpt3 = device(dev_class,
        description = 'Disc 3 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 8,
        offset = 70.30 + window_delay,
        unit = 'deg',
    ),
    cpt4 = device(dev_class,
        description = 'Disc 4 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 9,
        offset = 75.66 + window_delay,
        unit = 'deg',
    ),
    cpt5 = device(dev_class,
        description = 'Disc 5 index ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 10,
        offset = 266.60 + window_delay,
        unit = 'deg',
    ),
    cpt6 = device(dev_class,
        description = 'Disc 6 index ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 11,
        offset = 176.15 + window_delay,
        unit = 'deg',
    ),
)
