# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'setup for the status monitor for SANS-1'

group = 'special'


_sc1 = Block('Sample Changer 1', [
    BlockRow(
        Field(name='sc_y', dev='sc_y'),
    ),
    BlockRow(
        Field(name='SampleChanger', dev='sc1'),
    ),
    ],
    setups='sc1',
)

_sc2 = Block('Sample Changer 2', [
    BlockRow(
        Field(name='sc2_y', dev='sc_y'),
    ),
    BlockRow(
        Field(name='SampleChanger', dev='sc2'),
    ),
    ],
    setups='sc2',
)

_sc_t = Block('Temperature Sample Changer', [
    BlockRow(
        Field(name='sc_t_y', dev='sc_y'),
    ),
    BlockRow(
        Field(name='SampleChanger', dev='sc_t'),
    ),
    ],
    setups='sc_t',
)

_ccmsanssc = Block('Magnet Sample Changer', [
    BlockRow(
        Field(name='Position', dev='ccmsanssc_axis'),
    ),
    BlockRow(
        Field(name='SampleChanger', dev='ccmsanssc_position', format='%i'),
    ),
    BlockRow(
        Field(name='Switch', dev='ccmsanssc_switch'),
    ),
    ],
    setups='ccmsanssc',
)

_ccm2a2 = SetupBlock('ccm2a2')
_ccm2a2_temperature = SetupBlock('ccm2a2', 'temperatures')
_ccm2a2_plot = SetupBlock('ccm2a2', 'plot')

_ccm2a5 = SetupBlock('ccm2a5')
_ccm2a5_temperature = SetupBlock('ccm2a5', 'temperatures')
_ccm2a5_plot = SetupBlock('ccm2a5', 'plot')

_st = Block('Sample Table', [
    BlockRow(
        Field(name='st_phi', dev='st_phi'),
    ),
    BlockRow(
        Field(name='st_chi', dev='st_chi'),
    ),
    BlockRow(
        Field(name='st_omg', dev='st_omg'),
    ),
    BlockRow(
        Field(name='st_y', dev='st_y'),
    ),
    BlockRow(
        Field(name='st_z', dev='st_z'),
    ),
    BlockRow(
        Field(name='st_x', dev='st_x'),
    ),
    ],
    setups='sample_table',
)

_htf03 = Block('HTF03', [
    BlockRow(
        Field(name='Temperature', dev='T_htf03', format='%.2f', unit='C',
              width=12),
        Field(name='Target', key='t_htf03/target', format='%.2f', unit='C',
              width=12),
    ),
    BlockRow(
        Field(name='Setpoint', key='t_htf03/setpoint', format='%.1f',
              unit='C', width=12),
        Field(name='Heater Power', key='t_htf03/heaterpower',
              format='%.1f', unit='%', width=12),
        # Field(name='Vacuum', key='htf03_p'),
    ),
    BlockRow(
        Field(name='P', key='t_htf03/p', format='%i'),
        Field(name='I', key='t_htf03/i', format='%i'),
        Field(name='D', key='t_htf03/d', format='%i'),
    ),
    ],
    setups='htf03',
)

_htf03_plot = Block('HTF03 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_htf03', 'T_htf03/setpoint', 'T_htf03/target'],
              names=['30min', 'Setpoint', 'Target'],
              legend=True),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_htf03', 'T_htf03/setpoint', 'T_htf03/target'],
              names=['12h', 'Setpoint', 'Target'],
              legend=True),
    ),
    ],
    setups='htf03',
)

_htf01 = Block('HTF01', [
    BlockRow(
        Field(name='Temperature', dev='T_htf01', format='%.2f', unit='C',
              width=12),
        Field(name='Target', key='t_htf01/target', format='%.2f',
              unit='C', width=12),
    ),
    BlockRow(
        Field(name='Setpoint', key='t_htf01/setpoint', format='%.1f',
              unit='C', width=12),
        Field(name='Heater Power', key='t_htf01/heaterpower',
              format='%.1f', unit='%', width=12),
        # Field(name='Vacuum', key='htf01_p'),
    ),
    BlockRow(
        Field(name='P', key='t_htf01/p', format='%i'),
        Field(name='I', key='t_htf01/i', format='%i'),
        Field(name='D', key='t_htf01/d', format='%i'),
    ),
    ],
    setups='htf01',
)

_htf01_plot = Block('HTF01 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_htf01', 'T_htf01/setpoint', 'T_htf01/target'],
              names=['30min', 'Setpoint', 'Target'],
              legend=True),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_htf01', 'T_htf01/setpoint', 'T_htf01/target'],
              names=['12h', 'Setpoint', 'Target'],
              legend=True),
    ),
    ],
    setups='htf01',
)

_irf01 = Block('IRF01', [
    BlockRow(
        Field(name='Temperature', dev='T_irf01', format='%.2f', unit='C',
              width=12),
        Field(name='Target', key='t_irf01/target', format='%.2f',
              unit='C', width=12),
    ),
    BlockRow(
        Field(name='Setpoint', key='t_irf01/setpoint', format='%.1f',
              unit='C', width=12),
        Field(name='Heater Power', key='t_irf01/heaterpower',
              format='%.1f', unit='%', width=12),
        # Field(name='Vacuum', key='htf03_p'),
    ),
    BlockRow(
        Field(name='P', key='t_irf01/p', format='%i'),
        Field(name='I', key='t_irf01/i', format='%i'),
        Field(name='D', key='t_irf01/d', format='%i'),
    ),
    ],
    setups='irf01',
)

_irf10 = Block('IRF10', [
    BlockRow(
        Field(name='Temperature', dev='T_irf10', format='%.2f', unit='C',
              width=12),
        Field(name='Target', key='t_irf10/target', format='%.2f',
              unit='C', width=12),
    ),
    BlockRow(
        Field(name='Setpoint', key='t_irf10/setpoint', format='%.1f',
              unit='C', width=12),
        Field(name='Heater Power', key='t_irf10/heaterpower',
              format='%.1f', unit='%', width=12),
        # Field(name='Vacuum', key='htf03_p'),
    ),
    BlockRow(
        Field(name='P', key='t_irf10/p', format='%i'),
        Field(name='I', key='t_irf10/i', format='%i'),
        Field(name='D', key='t_irf10/d', format='%i'),
    ),
    ],
    setups='irf10',
)

_irf01_plot = Block('IRF01 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_irf01', 't_irf01/setpoint', 't_irf01/target'],
              names=['30min', 'Setpoint', 'Target'],
              legend=True),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_irf01', 't_irf01/setpoint', 't_irf01/target'],
              names=['12h', 'Setpoint', 'Target'],
              legend=True),
    ),
    ],
    setups='irf01',
)

_irf10_plot = Block('IRF10 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_irf10', 't_irf10/setpoint', 't_irf10/target'],
              names=['30min', 'Setpoint', 'Target'],
              legend=True),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_irf10', 't_irf10/setpoint', 't_irf10/target'],
              names=['12h', 'Setpoint', 'Target'],
              legend=True),
    ),
    ],
    setups='irf10',
)

_ccm5h = SetupBlock('ccm5h')
_ccm5h_temperature = SetupBlock('ccm5h', 'temperatures')
_ccm5h_plot = SetupBlock('ccm5h', 'plot')

_miramagnet = SetupBlock('miramagnet')
_miramagnet_plot = SetupBlock('miramagnet', 'plot')

_amagnet = SetupBlock('amagnet')
_amagnet_plot = SetupBlock('amagnet', 'plot')

_spinflipper = Block('Spin Flipper', [
    BlockRow(
        Field(name='P', dev='P_spinflipper'),
        # Field(name='F_spinflipper', dev='F_spinflipper'),
    ),
    BlockRow(
        Field(name='Forward', key='P_spinflipper/forward', unitkey='W'),
        Field(name='Reverse', key='P_spinflipper/reverse', unitkey='W'),
    ),
    BlockRow(
        #Field(name='Temperature', dev='T_spinflipper'),
        Field(name='Voltage', dev='U_spinflipper'),
    ),
    BlockRow(
        Field(name='A_spinflipper_hp', dev='A_spinflipper_hp'),
        Field(name='F_spinflipper_hp', dev='F_spinflipper_hp'),
    ),
    ],
    setups='spinflip',
)

rscs = [SetupBlock(rsc) for rsc in configdata('config_frm2.all_rscs')]

ccrs = [SetupBlock(ccr) for ccr in configdata('config_frm2.all_ccrs')]

T_Ts_plot = [
    Block('30min T and Ts plot', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=35, height=20, plotwindow=30*60,
                  devices=['T', 'Ts', 'T/setpoint', 'T/target'],
                  names=['T', 'Ts', 'Setpoint', 'Target'],
                  legend=True),
        ),
        ],
        setups='ccr*',
    )
]

cryos = [SetupBlock(cryo) for cryo in configdata('config_frm2.all_ccis')]

_sans1reactor = Column(
    Block('Reactor', [
        BlockRow(
            Field(name='Reactor', dev='ReactorPower'),
            Field(name='6 Fold Shutter', dev='Sixfold'),
            Field(name='NL4a', dev='NL4a'),
        ),
        ],
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
            Field(name='T in', dev='t_in_memograph', unit='C', width=6.5),
            Field(name='T out', dev='t_out_memograph', unit='C', width=6.5),
            Field(name='Cooling', dev='cooling_memograph', unit='kW',
                  width=6.5),
            Field(name='Flow in', dev='flow_in_memograph', unit='l/min',
                  width=6.5),
            Field(name='Flow out', dev='flow_out_memograph', unit='l/min',
                  width=6.5),
            Field(name='Leakage', dev='leak_memograph', unit='l/min',
                  width=6.5),
            Field(name='P in', dev='p_in_memograph', unit='bar',
                  width=6.5),
            Field(name='P out', dev='p_out_memograph', unit='bar',
                  width=6.5),
        ),
        ],
    ),
)

_sans1crane = Column(
    Block('Crane', [
        BlockRow(
            Field(name='Crane Pos', dev='Crane'),
        ),
        ],
    ),
)


_sans1julabo = Block('Julabo', [
    BlockRow(
        Field(name='Temperature Intern', dev='T_julabo_intern',
              format='%.2f', unit='C', width=16),
        Field(name='Target Intern', key='T_julabo_intern/target',
              format='%.2f', unit='C', width=16),
    ),
    BlockRow(
        Field(name='Setpoint Intern', key='T_julabo_intern/setpoint',
              format='%.1f', unit='C', width=16),
        Field(name='Heater Power Intern',
              key='T_julabo_intern/heateroutput', format='%.1f', unit='%',
              width=16),
    ),
    BlockRow(
        Field(name='P Intern', key='T_julabo_intern/p', format='%.2f'),
        Field(name='I Intern', key='T_julabo_intern/i', format='%i'),
        Field(name='D Intern', key='T_julabo_intern/d', format='%i'),
    ),
    BlockRow(
        Field(name='Temperature Extern', dev='T_julabo_extern',
              format='%.2f', unit='C', width=16),
        Field(name='Target Extern', key='T_julabo_extern/target',
              format='%.2f', unit='C', width=16),
    ),
    BlockRow(
        Field(name='Setpoint Extern', key='T_julabo_extern/setpoint',
              format='%.1f', unit='C', width=16),
        Field(name='Heater Power Extern',
              key='T_julabo_extern/heateroutput', format='%.1f', unit='%',
              width=16),
    ),
    BlockRow(
        Field(name='P Extern', key='T_julabo_extern/p', format='%.2f'),
        Field(name='I Extern', key='T_julabo_extern/i', format='%i'),
        Field(name='D Extern', key='T_julabo_extern/d', format='%i'),
    ),
    ],
    setups='julabo',
)

_julabo_plot = Block('Julabo plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=30, plotwindow=1800,
              devices=['T_julabo_intern', 'T_julabo_extern'],
              names=['T intern 30min','T extern 30min'],
              legend=True),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=30, plotwindow=12*3600,
              devices=['T_julabo_intern', 'T_julabo_extern'],
              names=['T intern 12h','T extern 12h'],
              legend=True),
    ),
    ],
    setups='julabo',
)

_dilato = Block('Dilatometer', [
    BlockRow(
        Field(name='Temperature', dev='Ts_dil',
              format='%.2f', unit='C', width=14),
        Field(name='Set Temp', dev='dil_set_temp',
              format='%.2f', unit='C', width=14),
    ),
    BlockRow(
        Field(name='Length change', dev='dil_dl',
              format='%.2f', unit='um', width=14),
        Field(name='Force', dev='dil_force',
              format='%.2f', unit='N', width=14),
    ),
    BlockRow(
        Field(name='Power', dev='dil_power',
              format='%.2f', unit='%', width=14),
        Field(name='Time', dev='dil_time',
              format='%.2f', unit='s', width=14),
    ),
    ],
    setups='dilato',
)

_dilato_plot = Block('Dilatometer plot temperature', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=33, height=20, plotwindow=1800,
              devices=['Ts_dil', 'dil_set_temp'],
              names=['30min', 'Setpoint'],
              legend=True),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=33, height=20, plotwindow=12*3600,
              devices=['Ts_dil', 'dil_set_temp'],
              names=['12h', 'Setpoint'],
              legend=True),
    ),
    ],
    setups='dilato',
)

_dilato_plot2 = Block('Dilatometer plot length change', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=30, height=20, plotwindow=1800,
              devices=['dil_dl'],
              names=['30min'],
              legend=True),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=30, height=20, plotwindow=12*3600,
              devices=['dil_dl'],
              names=['12h'],
              legend=True),
    ),
    ],
    setups='dilato',
)

_dilato_plot3 = Block('Dilatometer plot force', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=30, height=20, plotwindow=1800,
              devices=['dil_force'],
              names=['30min'],
              legend=True),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=30, height=20, plotwindow=12*3600,
              devices=['dil_force'],
              names=['12h'],
              legend=True),
    ),
    ],
    setups='dilato',
)

_pressure_box = Block('Pressure', [
    BlockRow(
        Field(name='Pressure', dev='pressure_box', width=12),
    ),
    ],
    setups='pressure_box',
)

_pressure_box_plot = Block('Pressure plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=1800,
              devices=['pressure_box'],
              names=['30min'],
              legend=True),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=12*3600,
              devices=['pressure_box'],
              names=['12h'],
              legend=True),
    ),
    ],
    setups='pressure_box',
)

_fg1 = Block('FG 1 - Sample', [
    BlockRow(
        Field(name='On/Off', dev='tisane_fg1_sample', width=12),
        Field(name='Frequency', key='tisane_fg1_sample/frequency', format='%.3f',
              unit='Hz', width=12),
    ),
    BlockRow(
        Field(name='Amplitude', key='tisane_fg1_sample/amplitude', format='%.2f',
              unit='V', width=12),
        Field(name='Offset', key='tisane_fg1_sample/offset', format='%.2f',
              unit='V', width=12),
    ),
    BlockRow(
        Field(name='Shape', key='tisane_fg1_sample/shape', width=12),
        Field(name='Dutycycle', key='tisane_fg1_sample/duty', format='%i',
              unit='%', width=12),
    ),
    ],
    setups='frequency',
)

_fg2 = Block('FG 2 - Detector', [
    BlockRow(
        Field(name='On/Off', dev='tisane_fg2_det', width=12),
        Field(name='Frequency', key='tisane_fg2_det/frequency', format='%.3f',
              unit='Hz', width=12),
    ),
    BlockRow(
        Field(name='Amplitude', key='tisane_fg2_det/amplitude', format='%.2f',
              unit='V', width=12),
        Field(name='Offset', key='tisane_fg2_det/offset', format='%.2f',
              unit='V', width=12),
    ),
    BlockRow(
        Field(name='Shape', key='tisane_fg2_det/shape', width=12),
        Field(name='Dutycycle', key='tisane_fg2_det/duty', format='%i',
              unit='%', width=12),
    ),
    ],
    setups='frequency',
)

_fc = Block('TISANE FC', [
    BlockRow(
        Field(name='Frequency', dev='tisane_fc', format='%.2e', width=12),
    ),
    ],
    setups='frequency',
)

_tisane_counts = Block('TISANE Counts', [
    BlockRow(
        Field(name='Counts', dev='TISANE_det_pulses', width=12),
    ),
    ],
    setups='tisane',
)

_helios01 = SetupBlock('helios01')

wuts = [SetupBlock(wut) for wut in ['wut-0-10-01', 'wut-0-10-02', 'wut-4-20-01', 'wut-4-20-02']]

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        description = 'Status monitor',
        showwatchdog = False,
        title = 'SANS-1 status monitor 2',
        cache = 'ctrl.sans1.frm2.tum.de',
        font = 'Luxi Sans',
        fontsize = 11,  # 12
        loglevel = 'info',
        padding = 0,  # 3
        prefix = 'nicos/',
        valuefont = 'Consolas',
        layout = [
            Row(_sans1reactor, _sans1general, _sans1crane),
            Row(
                Column(_ccmsanssc),
                Column(_sc1, _sc2, _sc_t, _st, *rscs),
                Column(_tisane_counts, _fg1, _helios01),
                Column(_fc, _fg2),
                Column(_htf01, _htf03, _irf01, _irf10,
                       _ccm2a2, _ccm2a2_temperature,
                       _ccm2a5, _ccm2a5_temperature,
                       _ccm5h, _ccm5h_temperature,
                       _miramagnet, _amagnet,
                       _sans1julabo, _dilato, _pressure_box),
                Column(_htf01_plot, _htf03_plot,
                       _irf01_plot, _irf10_plot,
                       _spinflipper, _julabo_plot,
                       _dilato_plot, _pressure_box_plot),
                Column(*ccrs),
                Column(*cryos),
                Column(*wuts),
            ),
            Row(
                Column(_dilato_plot2),
                Column(_dilato_plot3),
            ),
            Row(
                Column(_ccm5h_plot, _miramagnet_plot,
                       _amagnet_plot, _ccm2a2_plot, _ccm2a5_plot),
                Column(*T_Ts_plot),
            ),
        ],
    ),
)
