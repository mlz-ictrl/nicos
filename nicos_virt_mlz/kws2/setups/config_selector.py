description = 'preset values for the velocity selector'
group = 'configdata'

SELECTOR_PRESETS = {
    '2.9A tilt':  dict(lam=2.9,  spread=0.2, speed=26565, tilted=True),
    '4.66A':      dict(lam=4.66, spread=0.1, speed=27307, tilted=False),
    '5A':         dict(lam=5,    spread=0.1, speed=25428, tilted=False),
    '5A tilt':    dict(lam=5,    spread=0.2, speed=13946, tilted=True),
    '7A':         dict(lam=7,    spread=0.1, speed=18102, tilted=False),
    '7A tilt':    dict(lam=7,    spread=0.2, speed=9602,  tilted=True),
    '10A':        dict(lam=10,   spread=0.1, speed=12640, tilted=False),
    '19A':        dict(lam=19,   spread=0.1, speed=6634,  tilted=False),
}
