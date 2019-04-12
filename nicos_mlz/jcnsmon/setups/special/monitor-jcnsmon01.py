description = 'setup for the status monitor'
group = 'special'

## 8T Magnet ccm8v ##
ccm8v = Block('8T magnet', [
    BlockRow(Field(name='Field', dev='se/B_ccm8v'),
             Field(name='Hall', dev='se/ccm8v_Bhall')),
    '---',
    BlockRow(Field(name='VTI', dev='se/T_ccm8v_vti'),
             Field(name='VTI heat', dev='se/ccm8v_vti_heater'),
             Field(name='VTI NV', dev='se/ccm8v_vti_nv')),
    BlockRow(Field(name='Stick', dev='se/T_ccm8v_stick'),
             Field(name='Stick heat', dev='se/ccm8v_stick_heater')),
    '---',
    BlockRow(Field(name='Coils', dev='se/ccm8v_Tmag'),
             Field(name='Dewar', dev='se/ccm8v_pdewar', unit=' '),
             Field(name='Coldhead', dev='se/ccm8v_Tcoldhead')),
    BlockRow(Field(name='LHe', dev='se/ccm8v_LHe'),
             Field(name='LN2', dev='se/ccm8v_LN2')),
])

## SPHERES CRYO ##
jlc22_1 = Block('SPHERES CRYO', [
        BlockRow(Field(name='pressure', dev='se/jlc22_c_pressure'),
                 Field(name='T tube', dev='se/jlc22_T_sample', unit='K')
                 )
])

## SPHERES CRYO PLOT ##
jlc22_2 = Block('SPHERES CRYO2', [
        BlockRow(Field(name='pressure', dev='se/jlc22_c_pressure'),
                 Field(name='T tube', dev='se/jlc22_T_sample', unit='K'),
                 ),
        BlockRow(Field(plot='temp', name='T sample', key='se/jlc22_T_sample/value', plotwindow=3600, width=30, height=20),
                 Field(plot='temp', name='T tube', key='se/jlc22_T_tube/value'),
                )
])


layout = [     Row(Column(ccm8v),Column(jlc22_2))    ]


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = '',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 25,
        padding = 3,
        layout = layout,
        expectmaster = False,
    ),
)
