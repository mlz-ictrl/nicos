'''
Created on Apr 23, 2015

@author: pedersen
'''

description = 'Virtual temperature, use this if no readable cryo controller is used.'
group = 'lowlevel'
includes = ['alias_T']

devices = dict(
    T_manual = device('devices.generic.manual.ManualMove',
                      description = 'sample temperature (no cryo)',
                      default = 297.0,
                      abslimits = (0, 5000),
                      unit = 'K',
                      fmtstr = '%.0f',
                     ),
)
startupcode = """
T.alias = T_manual
Ts.alias = T_manual
AddEnvironment(T, Ts)
"""

