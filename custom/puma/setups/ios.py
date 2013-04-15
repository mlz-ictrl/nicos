#  -*- coding: utf-8 -*-

description = 'Atenuator and PGFilter'


includes = ['system', 'motorbus8']



devices = dict(

   att_sw = device('devices.vendor.ipc.Input',
                description = '...',
                bus = 'motorbus8',
                addr = 104,
                first = 0,
                last = 9,
                unit = ''),
   att_press = device('devices.vendor.ipc.Input',
                bus = 'motorbus8',
                addr = 103,
                first = 13,
                last = 13,
                unit = ''),
   att_set = device('devices.vendor.ipc.Output',
                bus = 'motorbus8',
                addr = 114,
                first = 3,
                last = 7,
                unit = ''),

   atn = device('puma.attenuator.Attenuator',
                io_status = 'att_sw',
                io_set = 'att_set',
                io_press = 'att_press',
                abslimits = (0, 38),
                unit = 'mm'),

   fpg_sw = device('devices.vendor.ipc.Input',
                description = '...',
                bus = 'motorbus8',
                addr = 103,
                first = 14,
                last = 15,
                unit = ''),

   fpg_set = device('devices.vendor.ipc.Output',
                bus = 'motorbus8',
                addr = 114,
                first = 2,
                last = 2,
                unit = ''),

   fpg = device('puma.pgfilter.PGFilter',
                io_status = 'fpg_sw',
                io_set = 'fpg_set',
                unit = ''),
)
