description = 'sample tranlation Z'

group = 'optional'

includes = []

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

devices = dict(
    zs = device('nicos.devices.vendor.caress.Motor',
                description = 'HWB ZS',
                fmtstr = '%.2f',
                unit = 'mm',
                coderoffset = 0,
                abslimits = (-20, 20),
                nameserver = '%s' % (nameservice,),
                objname = '%s' % (servername),
                config = 'ZS 115 11 0x00f1e000 3 5000 1000 100 1 0 50 '
                         '-1 0 1 4000 1 10 10 0 500',
               ),
)

alias_config = {
}
