# -*- coding: utf-8 -*-

# NICOS test setup

name = 'test setup with a few devices'

modules = ['nicm.commands']

devices = dict(
    m1 = device('nicm.testdev.VirtualMotor',
                autocreate = False,
                loglevel = 'info',
                initval = 1,
                unit = 'deg'),

    m2 = device('nicm.testdev.VirtualMotor',
                autocreate = False,
                loglevel = 'debug',
                initval = 0.5,
                unit = 'deg'),

    c1 = device('nicm.testdev.VirtualCoder',
                autocreate = False,
                unit = 'deg'),

    a1 = device('nicm.axis.Axis',
                adev = {'motor': 'm1', 'coder': 'c1', 'obs': ['c1']},
                absMin = 0,
                absMax = 100,
                userMin = 0,
                userMax = 50),

    a2 = device('nicm.axis.Axis',
                adev = {'motor': 'm2', 'coder': 'c1', 'obs': []},
                absMin = 0,
                absMax = 100,
                userMin = 0,
                userMax = 50),
)

startupcode = '''
print 'startup code executed'
'''
