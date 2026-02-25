description = 'POLI sample table'

group = 'lowlevel'

includes = ['alias_sth']

tango_base = 'tango://phys.poli.frm2:10000/poli/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    omega = device('nicos.devices.entangle.MotorAxis',
        description = 'table omega axis',
        tangodevice = s7_motor + 'omega',
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    gamma = device('nicos.devices.entangle.MotorAxis',
        description = 'table gamma axis',
        tangodevice = s7_motor + 'gamma',
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    chi1 = device('nicos.devices.entangle.MotorAxis',
        description = 'table chi1 axis',
        tangodevice = s7_motor + 'chi1',
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    chi2 = device('nicos.devices.entangle.MotorAxis',
        description = 'table chi2 axis',
        tangodevice = s7_motor + 'chi2',
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    xtrans = device('nicos.devices.entangle.MotorAxis',
        description = 'table x translation axis',
        tangodevice = s7_motor + 'xtrans',
        unit = 'mm',
        fmtstr = '%.2f',
        precision = 0.01,
    ),
    ytrans = device('nicos.devices.entangle.MotorAxis',
        description = 'table y translation axis',
        tangodevice = s7_motor + 'ytrans',
        unit = 'mm',
        fmtstr = '%.2f',
        precision = 0.01,
    ),
)

alias_config = {
    'sth': {'omega': 100}
}
