description = 'Cryo control box'
includes = ['system']

devices = dict(
    cryo_g = device('nicos.taco.io.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/gas'),
    cryo_v = device('nicos.taco.io.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/vacuum'),
    cryo_machine = device('nicos.taco.io.DigitalOutput',
                    tacodevice = '//toftofsrv/toftof/ccr/compressor'),
    cryo_p = device('nicos.taco.io.AnalogInput',
                    tacodevice = '//toftofsrv/toftof/ccr/p1'),
)
