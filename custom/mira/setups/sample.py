description = 'sample table'
group = 'lowlevel'

includes = ['alias_sth']

devices = dict(
    phi      = device('devices.taco.HoveringAxis',
                      description = 'sample two-theta angle',
                      tacodevice = '//mirasrv/mira/axis/phi',
                      abslimits = (-120, 120),
                      startdelay = 1,
                      stopdelay = 2,
                      switch = 'air_sample',
                      switchvalues = (0, 1),
                      fmtstr = '%.3f',
                     ),

    air_mono   = device('devices.taco.DigitalOutput',
                        tacodevice = '//mirasrv/mira/phytronio/air_mono',
                        lowlevel = True,
                       ),

    air_sample = device('mira.refcountio.RefcountDigitalOutput',
                        tacodevice = '//mirasrv/mira/phytronio/air_sample',
                        lowlevel = True,
                       ),

    air_ana    = device('mira.refcountio.RefcountDigitalOutput',
                        tacodevice = '//mirasrv/mira/phytronio/air_det',
                        lowlevel = True,
                       ),

    om       = device('mira.phytron.Axis',
                      description = 'sample theta angle',
                      tacodevice = '//mirasrv/mira/axis/om',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f',
                     ),
    stx      = device('mira.phytron.Axis',
                      description = 'sample translation along the beam (for om=0)',
                      tacodevice = '//mirasrv/mira/axis/stx',
                      abslimits = (-25, 25),
                      fmtstr = '%.2f',
                     ),
    sty      = device('mira.phytron.Axis',
                      description = 'sample translation horizontally perpendicular to the beam (for om=0)',
                      tacodevice = '//mirasrv/mira/axis/sty',
                      abslimits = (-25, 25),
                      fmtstr = '%.2f',
                     ),
    stz      = device('mira.phytron.Axis',
                      description = 'sample translation in vertical direction',
                      tacodevice = '//mirasrv/mira/axis/stz',
                      abslimits = (0, 40),
                      fmtstr = '%.2f',
                     ),
    sgx      = device('mira.phytron.Axis',
                      description = 'sample tilt around beam axis (for om=0)',
                      tacodevice = '//mirasrv/mira/axis/sgx',
                      abslimits = (-5, 5),
                      fmtstr = '%.2f',
                     ),
    sgy      = device('mira.phytron.Axis',
                      description = 'sample tilt orthogonal to beam axis (for om=0)',
                      tacodevice = '//mirasrv/mira/axis/sgy',
                      abslimits = (-5, 5),
                      fmtstr = '%.2f',
                     ),
)

alias_config = {
    'sth': {'om': 0},
}
