description = 'test beckhoff setup'
group = 'hidden'

devices = dict(
  bh1 = device('nicos.mira.beckhoff.BeckhoffDigitalOutput',
               tacodevice = 'mira/modbus/beckhoff',
               startoffset = 0,
               bitwidth = 32),
  bh2 = device('nicos.mira.beckhoff.BeckhoffDigitalOutput',
               tacodevice = 'mira/modbus/beckhoff',
               startoffset = 32,
               bitwidth = 32),
)
