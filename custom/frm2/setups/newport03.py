description = 'Newport sample stick rotator'

group = 'optional'

includes = ['system', 'alias_sth']

nethost = 'newport03'

devices = {
    'sth_%s' % nethost : device('devices.taco.Motor',
                                tacodevice = '//%s/newport/newportmc/motor' % (nethost,),
                               ),
}

startupcode = """
sth.alias = sth_%s
""" % (nethost,)
