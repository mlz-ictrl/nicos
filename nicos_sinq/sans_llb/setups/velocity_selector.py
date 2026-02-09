description = 'Devices for the velocity selector'

group = 'lowlevel'

forbidden = [(3400, 4700), (8500, 11_500), (28_400, 31_000)]

devices = dict(
    velocity_selector = device('nicos_sinq.sans_llb.devices.velocity_selector.VelocitySelectorLLB',
        description = 'Velocity Selector',
        fmtstr = '%d',
        vspv = 'SQ:SANS-LLB:VS',
        epicstimeout = 3.0,
        precision = 20,
        forbidden_regions = forbidden,
    ),
    wavelength = device('nicos_sinq.sans_llb.devices.wavelength.SANSWL',
        description = 'Device which translates wavelength to'
        'VS speed',
        a = 0.0165, # VLB: 08.12.2025 values updated after the calibration with the chopper
        b = 8728.1,
        #a = 0.012,
        #b = 8923.7, # VLB: 07.08.2024 values updated after the calibration with the chopper
        speed = 'velocity_selector',
        unit = 'nm'
    ),
)
