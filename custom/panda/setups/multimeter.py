description = 'HP34420 multimeter readout'
group = 'optional'

devices = dict(
    R = device('nicos.devices.taco.AnalogInput',
               description = 'multimeter readout',
               tacodevice = '//phys.panda.frm2/panda/hp34420/resistance',
              ),
)
