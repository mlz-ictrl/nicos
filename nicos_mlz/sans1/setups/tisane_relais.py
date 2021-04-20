description = 'tisane relais for SANS1'

group = 'optional'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
    tisane_relais = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'wutrelais/relais',
        description = 'TISANE trigger relais',
    ),
)
