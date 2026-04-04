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
                   visibility = colx1_conf['visibility'],
                   unit = colx1_conf['unit'],
                   ),
    colx2 = device('nicos.devices.entangle.Motor',
                   description = colx2_conf['description'],
                   tangodevice = tango_base+'device/axis/colx2',
                   precision = colx2_conf['precision'],
                   visibility = colx2_conf['visibility'],
                   unit = colx2_conf['unit'],
                   ),
    coly1 = device('nicos.devices.entangle.Motor',
                   description = coly1_conf['description'],
                   tangodevice = tango_base+'device/axis/coly1',
                   precision = coly1_conf['precision'],
                   visibility = coly1_conf['visibility'],
                   unit = coly1_conf['unit'],
                   ),
    coly2 = device('nicos.devices.entangle.Motor',
                   description = coly2_conf['description'],
                   tangodevice = tango_base+'device/axis/coly2',
                   precision = coly2_conf['precision'],
                   visibility = coly2_conf['visibility'],
                   unit = coly2_conf['unit'],
                   ),
)
