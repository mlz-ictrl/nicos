description = 'Newport sample stick rotator'

includes = ['system']

devices = dict(
    stick = device('nicos.taco.Motor',
                   tacodevice = '//toftofsrv/toftof/stick/motor'),
)
