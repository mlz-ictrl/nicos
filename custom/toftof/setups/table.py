description = 'sample table'
includes = ['system']

nethost= '//toftofsrv.toftof.frm2/'

devices = dict(
    gx   = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gxm',
                  fmtstr = "%7.3f",
                  abslimits = (-20.0, 20.)),
    gy   = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gym',
                  fmtstr = "%7.3f",
                  abslimits = (-20.0, 20.)),
    gz   = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gzm',
                  fmtstr = "%7.3f",
                  abslimits = (-14.8, 50.)),
    gcx  = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gcxm',
                  fmtstr = "%7.3f",
                  abslimits = (-20.0, 20.)),
    gcy  = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gcym',
                  fmtstr = "%7.3f",
                  abslimits = (-20.0, 20.)),
    gphi = device('nicos.taco.motor.Motor',
                  tacodevice = nethost + 'toftof/huber/gphim',
                  fmtstr = "%7.3f",
                  abslimits = (-20.0, 150.)),
)
