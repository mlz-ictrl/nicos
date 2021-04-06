#  -*- coding: utf-8 -*-
description = 'Oscilloscope RTE1104 for reading the RMS values of all 4RF coils'

group = 'optional'

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = {
    'rte1104_io': device('nicos.devices.tango.StringIO',
        tangodevice = tango_base + 'rte1104/io',
        lowlevel = True,
    ),
}

startupcode = """
CreateDevice('rte1104_io')
rte1104_io.writeLine("MMEM:RCL 'C:\\\\users\\\\Public\\\\Documents\\\\Rohde-Schwarz\\\\RTx\\\\SaveSets\\\\RTE1104_Settings_NRSE_default.dfl'")
"""
