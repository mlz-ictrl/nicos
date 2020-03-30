description = 'Chopper phase timing, readout for light barrier and coder index'

group = 'lowlevel'

window_delay = -120

all_lowlevel = False  # or True

instrument_values = configdata('instrument.values')

URL = (instrument_values['url_base'] % 'cpt') + 'json-visual'
code_base = instrument_values['code_base']  + 'gkssjson.CPTReadout'

devices = dict(
    cpt0 = device(code_base,
        description = 'Disc 1 light barrier ' + description + ' Phase of Disk1!',
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = -1,
        offset = 0.0,
        unit = 'deg',
        lowlevel = True,
    ),
    cpt1 = device(code_base,
        description = 'Disc 1 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 0,
        # offset = 0,
        unit = 'rpm',
    ),
    cpt2 = device(code_base,
         description = 'Disc 2 light barrier ' + description,
         url = URL,
         valuekey = 'chopper_act',
         timeout = 3.0,
         channel = 7,
         offset = 28.44 + window_delay,
         unit = 'deg',
     ),
    cpt3 = device(code_base,
        description = 'Disc 3 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 8,
        offset = 70.30 + window_delay,
        unit = 'deg',
    ),
    cpt4 = device(code_base,
        description = 'Disc 4 light barrier ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 9,
        offset = 75.66 + window_delay,
        unit = 'deg',
    ),
    cpt5 = device(code_base,
        description = 'Disc 5 index ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 10,
        offset = 266.60 + window_delay,
        unit = 'deg',
    ),
    cpt6 = device(code_base,
        description = 'Disc 6 index ' + description,
        url = URL,
        valuekey = 'chopper_act',
        timeout = 3.0,
        channel = 11,
        offset = 176.15 + window_delay,
        unit = 'deg',
    ),
)
