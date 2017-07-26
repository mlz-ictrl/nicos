#
# The sample changer at SANS1 consists of two components:
# - the horizontal move axis which is mounted on top of the sample table
# - the vertical move axis which is part of the sample tables itself.
#
description = 'sample changer devices'

group = 'optional'

includes = ['system', 'table']

top = 28.0
bottom = -31.0

devices = dict(
    sc1_x = device('nicos.devices.generic.VirtualMotor',
                   lowlevel = True,
                   fmtstr = '%.2f',
                   abslimits = (0, 600),
                   jitter = 0.02,
                   speed = 10,
                   unit = 'mm',
                  ),

    sc1 = device('nicos.devices.generic.MultiSwitcher',
                 description = 'multi switcher demo',
                 moveables = ['sc1_x', 'z'],
                 mapping = {'1':  [594.5, bottom],  '2': [535.5, bottom],
                            '3':  [476.5, bottom],  '4': [417.5, bottom],
                            '5':  [358.5, bottom],  '6': [299.5, bottom],
                            '7':  [240.5, bottom],  '8': [181.5, bottom],
                            '9':  [122.5, bottom], '10': [ 63.5, bottom],
                            '11': [  4.5, bottom],
                            '12': [594.5, top], '13': [535.5, top],
                            '14': [476.5, top], '15': [417.5, top],
                            '16': [358.5, top], '17': [299.5, top],
                            '18': [240.5, top], '19': [181.5, top],
                            '20': [122.5, top], '21': [ 63.5, top],
                            '22': [  4.5, top],
                           },
                 precision = [0.05],
                 blockingmove = False,
                ),
)
