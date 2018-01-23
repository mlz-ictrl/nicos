description = 'GE detector setup PV values'
group = 'configdata'

EIGHT_PACKS = [
    # ('ep01', 'GE-DD590C-EP'), # replaced 2015/10/29
    ('ep01', 'GE-DD6D8C-EP'),
    ('ep02', 'GE-DD5FB3-EP'),
    ('ep03', 'GE-DDA871-EP'),
    ('ep04', 'GE-DD7D29-EP'),
    ('ep05', 'GE-DDBA8F-EP'),
    ('ep06', 'GE-DD5913-EP'),
    ('ep07', 'GE-DDC7CA-EP'),
    ('ep08', 'GE-DD6DEF-EP'),
    ('ep09', 'GE-DD5FB6-EP'),
    ('ep10', 'GE-DDBA88-EP'),
    # ('ep11', 'GE-DD6AE9-EP'),
    # ('ep11', 'GE-DD6D79-EP'), # was spare
    ('ep11', 'GE-DD9522-EP'),  # changed 2015/09/23
    ('ep12', 'GE-DD6D89-EP'),
    ('ep13', 'GE-DD6D96-EP'),
    ('ep14', 'GE-DD6974-EP'),
    ('ep15', 'GE-DD5FA9-EP'),
    ('ep16', 'GE-DDA874-EP'),
    ('ep17', 'GE-DD6975-EP'),
    ('ep18', 'GE-DD5916-EP'),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}
# -- To set different HVs for some 8-packs:
# HV_VALUES['ep01'] = 0
# HV_VALUES['ep18'] = 0

PV_SCALES = {
    'ep01': [('AScales', [2048, 1994, 2082, 2089, 2055, 2079, 2106, 2072]), ('Scales', [2048]*8)],
    'ep02': [('AScales', [2065, 2080, 2053, 2050, 2048, 2082, 2052, 2050]), ('Scales', [2048]*8)],
    'ep03': [('AScales', [2062, 2027, 2049, 2060, 2085, 1974, 1990, 2040]), ('Scales', [2048]*8)],
    'ep04': [('AScales', [2028, 1993, 2016, 2021, 2023, 2022, 2033, 2042]), ('Scales', [2048]*8)],
    'ep05': [('AScales', [2000, 2044, 1999, 2060, 2040, 2002, 2052, 2061]), ('Scales', [2048]*8)],
    'ep06': [('AScales', [2023, 2046, 2079, 2057, 2049, 2046, 2068, 2030]), ('Scales', [2048]*8)],
    'ep07': [('AScales', [2037, 2036, 1998, 2007, 2021, 2011, 1981, 2026]), ('Scales', [2048]*8)],
    'ep08': [('AScales', [2040, 2057, 2032, 2017, 2048, 2045, 2031, 2099]), ('Scales', [2048]*8)],
    'ep09': [('AScales', [2007, 2040, 1992, 2057, 2025, 2010, 2013, 1993]), ('Scales', [2048]*8)],
    'ep10': [('AScales', [2050, 2035, 2046, 2075, 2059, 2022, 2047, 2045]), ('Scales', [2048]*8)],
    'ep11': [('AScales', [2031, 2029, 2043, 2006, 2024, 2009, 2047, 2043]), ('Scales', [2048]*8)],
    'ep12': [('AScales', [2035, 2050, 2014, 2030, 2033, 2022, 2029, 2032]), ('Scales', [2048]*8)],
    'ep13': [('AScales', [2050, 2064, 2064, 2065, 2047, 2048, 2007, 2058]), ('Scales', [2048]*8)],
    'ep15': [('AScales', [2076, 2053, 2058, 2073, 2025, 2061, 2090, 2058]), ('Scales', [2048]*8)],
    'ep14': [('AScales', [2063, 2060, 2045, 2009, 2066, 2041, 2070, 2064]), ('Scales', [2048]*8)],
    'ep16': [('AScales', [2151, 2043, 2011, 2103, 2098, 2085, 2107, 2126]), ('Scales', [2048]*8)],
    'ep17': [('AScales', [2110, 2127, 2111, 2096, 2132, 2104, 2133, 2148]), ('Scales', [2048]*8)],
    'ep18': [('AScales', [2089, 2078, 2081, 1971, 2047, 2101, 2079, 2052]), ('Scales', [2048]*8)],
}

# -- For recalibration, set everything to defaults:
# PV_SCALES = {
#     'ep%02d' % i: [('AScales', [2048]*8), ('Scales', [2048]*8)] for i in range(1, 19)
# }

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ('Mode', MODE_DIAG),
    ('DecimationFactor', 1),
    ('DiscriminatorLevel', 1024),
    ('NegativeVeto', -16384),
    ('PositiveVeto', 16383),
    ('Sample1', 10),
    ('BScales', [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ('TubeEnables', [1, 1, 1, 1, 1, 1, 1, 1]),
    ('AccumulationLength', 60),
    ('WaveformCaptureLength', 1015),
]

# pixel per tube
PPT_S = 94
PPT_M = 206
PPT_L = 256

# -- For recalibration, set to max. pixel resolution:
# PPT_S = 1024
# PPT_M = 1024
# PPT_L = 1024

PV_VALUES_SINGLE = {
    'ep01': [('ModulePixelIdStart', 0*8192),  ('PixelCount', PPT_S)],
    'ep02': [('ModulePixelIdStart', 1*8192),  ('PixelCount', PPT_S)],
    'ep03': [('ModulePixelIdStart', 2*8192),  ('PixelCount', PPT_S)],
    'ep04': [('ModulePixelIdStart', 3*8192),  ('PixelCount', PPT_M)],
    'ep05': [('ModulePixelIdStart', 4*8192),  ('PixelCount', PPT_M)],
    'ep06': [('ModulePixelIdStart', 5*8192),  ('PixelCount', PPT_M)],
    'ep07': [('ModulePixelIdStart', 6*8192),  ('PixelCount', PPT_L)],
    'ep08': [('ModulePixelIdStart', 7*8192),  ('PixelCount', PPT_L)],
    'ep09': [('ModulePixelIdStart', 8*8192),  ('PixelCount', PPT_L)],
    'ep10': [('ModulePixelIdStart', 9*8192),  ('PixelCount', PPT_L)],
    'ep11': [('ModulePixelIdStart', 10*8192), ('PixelCount', PPT_L)],
    'ep12': [('ModulePixelIdStart', 11*8192), ('PixelCount', PPT_L)],
    'ep13': [('ModulePixelIdStart', 12*8192), ('PixelCount', PPT_M)],
    'ep14': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep15': [('ModulePixelIdStart', 13*8192), ('PixelCount', PPT_M)],
    'ep16': [('ModulePixelIdStart', 15*8192), ('PixelCount', PPT_S)],
    'ep17': [('ModulePixelIdStart', 16*8192), ('PixelCount', PPT_S)],
    'ep18': [('ModulePixelIdStart', 17*8192), ('PixelCount', PPT_S)],
}
