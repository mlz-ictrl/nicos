description = 'Switching from one capillary to the other'

includes = ['virtual_capillary_motors']

group = 'lowlevel'

devices = dict(
    capillary_selector = device('nicos_tuw.xccm.devices.capillary_selector.CapillarySelector',
        description = 'change between the two capillaries or have no capillary',
        moveables = ['cap_Ty','cap_Tz'],
        fallback = 0,
        fmtstr = '%d',
        mapping = {
            1: [0, 10],
            2: [10, 10],
            3: [5, 0],
            },
        # higher precision values to allow finetuning of position to user
        precision = [0.1, 0.1],
        ),
)
