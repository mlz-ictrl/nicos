description = 'Collimator movements'

tango_base = configdata('localconfig.tango_base')

colx1_conf = configdata('localconfig.COLX1_CONF')
colx2_conf = configdata('localconfig.COLX2_CONF')
coly1_conf = configdata('localconfig.COLY1_CONF')
coly2_conf = configdata('localconfig.COLY2_CONF')


devices = dict(
    colx1 = device('nicos.devices.entangle.Motor',
                   description = colx1_conf['description'],
                   tangodevice = tango_base+'device/axis/colx1',
                   precision = colx1_conf['precision'],
                   lowlevel = colx1_conf['lowlevel'],
                   abslimits = colx1_conf['abslimits'],
                   speed = colx1_conf['speed'],
                   unit = colx1_conf['unit'],
                   ),
    colx2 = device('nicos.devices.entangle.Motor',
                   description = colx2_conf['description'],
                   tangodevice = tango_base+'device/axis/colx2',
                   precision = colx2_conf['precision'],
                   lowlevel = colx2_conf['lowlevel'],
                   abslimits = colx2_conf['abslimits'],
                   speed = colx2_conf['speed'],
                   unit = colx2_conf['unit'],
                   ),
    coly1 = device('nicos.devices.entangle.Motor',
                   description = coly1_conf['description'],
                   tangodevice = tango_base+'device/axis/coly1',
                   precision = coly1_conf['precision'],
                   lowlevel = coly1_conf['lowlevel'],
                   abslimits = coly1_conf['abslimits'],
                   speed = coly1_conf['speed'],
                   unit = coly1_conf['unit'],
                   ),
    coly2 = device('nicos.devices.entangle.Motor',
                   description = coly2_conf['description'],
                   tangodevice = tango_base+'device/axis/coly2',
                   precision = coly2_conf['precision'],
                   lowlevel = coly2_conf['lowlevel'],
                   abslimits = coly2_conf['abslimits'],
                   speed = coly2_conf['speed'],
                   unit = coly2_conf['unit'],
                   ),
)
