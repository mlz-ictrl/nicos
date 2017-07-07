#  -*- coding: utf-8 -*-

description = 'Sample table (translation)'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    sgz_mot = device('devices.taco.Motor',
                        description = 'Sample goniometer: z (motor)',
                        tacodevice = '%s/husco1/motor7' % taco_base,
                        fmtstr = '%.3f',
                        lowlevel = True,
                        ),
    sgz_enc = device('devices.taco.Coder',
                      description = 'Sample goniometer: z (encoder)',
                      tacodevice = '%s/enc/probe_1' % taco_base,
                      fmtstr = '%.3f',
                      lowlevel = True,
                      ),
    sgz = device('devices.generic.Axis',
                  description = 'Sample goniometer: z',
                  motor = 'sgz_mot',
                  coder = 'sgz_enc',
                  fmtstr = '%.3f',
                  precision = 0.1,
                  ),
    stx = device('devices.taco.Motor',
                  description = 'Sample table: x',
                  tacodevice = '%s/husco1/motor3' % taco_base, # maybe motor4
                  fmtstr = '%.3f',
                  ),

    sty = device('devices.taco.Motor',
                  description = 'Sample table: y',
                  tacodevice = '%s/husco1/motor4' % taco_base, # maybe motor3
                  fmtstr = '%.3f',
                  ),

    sgx = device('devices.taco.Motor',
                   description = 'Sample goniometer: x',
                   tacodevice = '%s/husco1/motor5' % taco_base,
                   fmtstr = '%.3f',
                   ),
    sgy = device('devices.taco.Motor',
                   description = 'Sample goniometer: x',
                   tacodevice = '%s/husco1/motor6' % taco_base,
                   fmtstr = '%.3f',
                   ),
    st_air = device('devices.tango.NamedDigitalOutput',
                description='Sample table pressured air',
                tangodevice='%s/iobox/plc_air_sampletable' % tango_base,
                mapping={'on': 1, 'off': 0},
                ),
)
