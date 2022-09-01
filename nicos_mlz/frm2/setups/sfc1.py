
description = 'Cetoni syringe high pressure pumps, valves and pressure sensors.'

group = 'plugplay'

modules = ['nicos_mlz.frm2.commands.cetoni']

tango_base = f'tango://{setupname}:10000/box/'

_valve_states = {'inlet': 1,
                 'outlet': 2,
                 'pass_through': 3,
                 'closed': 4,}
devices = {
    # 'relief_valve': device('nicos.devices.entangle.Actuator',
    #     description = 'Valve 4',
    #     tangodevice = tango_base + 'beckhoff/output',
    #     fmtstr = '%.3f',
    #     pollinterval = 0.5,
    # ),
}
for i in range(1, 4):
    devices[f'pressure{i}'] = device('nicos_mlz.devices.cetoni.CetoniSensor',
        description = f'Sensor {i}',
        tangodevice = tango_base + f'pressure/sensor{i}',
        fmtstr = '%.2f',
        pollinterval = 300,
    )
    devices[f'pump{i}'] = device('nicos_mlz.devices.cetoni.CetoniPump',
        description = f'Pump {i}',
        tangodevice = tango_base + f'pumps/pump{i}',
        fmtstr = '%.3f',
        pollinterval = 300,
        pressure = f'pressure{i}',
        valve = f'valve{i}',
    )
    devices[f'valve{i}'] = device('nicos.devices.entangle.NamedDigitalOutput',
        description = f'Valve {i}',
        tangodevice = tango_base + f'valves/valve{i}',
        fmtstr = '%d',
        mapping = _valve_states,
        pollinterval = 300,)


def topic(cmd):
    return f'{cmd}_\n\n.. _{cmd}: cmd:{cmd}\n\n'

import importlib
excluded = ['helparglist', 'usercommand']
help_topics = {'Cetoni commands': ''}
for mod in modules:
    mod = importlib.import_module(mod)
    help_topics['Cetoni commands'] = help_topics['Cetoni commands'].join(
        [topic(i) for i in dir(mod) \
         if callable(getattr(mod, i)) and i not in excluded])
