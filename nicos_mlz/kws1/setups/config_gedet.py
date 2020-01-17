description = 'GE detector setup PV values'
group = 'configdata'

EIGHT_PACKS = [
    ('ep01', 'GE-D76A55-EP'),
    ('ep02', 'GE-D74199-EP'),
    ('ep03', 'GE-D7426B-EP'),
    ('ep04', 'GE-D76A68-EP'),
    ('ep05', 'GE-D74270-EP'),
    ('ep06', 'GE-D72EB0-EP'),
    ('ep07', 'GE-D72F9D-EP'),
    ('ep08', 'GE-D73043-EP'),
#    ('ep09x', 'GE-D7561E-EP'),
    ('ep09', 'GE-D71E2C-EP'),
#    ('ep10', 'GE-D72EA6-EP'), doesn't exist
    ('ep10x', 'GE-D72F49-EP'),
    ('ep11', 'GE-D75751-EP'),
    ('ep12', 'GE-D73046-EP'),
    ('ep13', 'GE-D75623-EP'),
    ('ep14', 'GE-D72F44-EP'),
    ('ep15x', 'GE-D76A5A-EP'),
#    ('ep15', 'GE-D7304D-EP'), damaged tube
    ('ep16', 'GE-D74372-EP'),
    ('ep17', 'GE-D7436D-EP'),
    ('ep18', 'GE-D76A50-EP'),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}
# -- To set different HVs for some 8-packs:
# HV_VALUES['ep01'] = 0

PV_SCALES = {
#    'ep09x': [('AScales', [2082, 2074, 2055, 2058, 2120, 2112, 2105, 2094]),('Scales', [2060, 2057, 2039, 2039, 2052, 2062, 2062, 2066])],
#    'ep10': [('AScales', [2083, 2022, 2069, 2052, 2045, 2048, 2044, 2039]), ('Scales', [2077, 2078, 2059, 2061, 2055, 2060, 2034, 2065])],
#    'ep15': [('AScales', [2083, 2145, 2104, 2069, 2105, 2083, 2106, 2109]), ('Scales', [2075, 2090, 2072, 2079, 2062, 2072, 2084, 2067])],
    'ep01': [('AScales', [2158, 2061, 2059, 2076, 2117, 2074, 2091, 2092]), ('Scales', [2245, 2239, 2226, 2259, 2236, 2245, 2240, 2236])],
    'ep02': [('AScales', [2078, 2090, 2123, 2147, 2076, 2090, 2086, 2086]), ('Scales', [2234, 2225, 2242, 2235, 2228, 2223, 2223, 2210])],
    'ep03': [('AScales', [2081, 2077, 2082, 2026, 2053, 2052, 2081, 2063]), ('Scales', [2218, 2247, 2245, 2229, 2238, 2241, 2247, 2251])],
    'ep04': [('AScales', [2113, 2114, 2101, 2060, 2054, 2068, 2068, 2067]), ('Scales', [2049, 2055, 2070, 2068, 2070, 2069, 2054, 2072])],
    'ep05': [('AScales', [2008, 2024, 2053, 2046, 2083, 2075, 2068, 2074]), ('Scales', [2058, 2056, 2064, 2061, 2082, 2082, 2077, 2070])],
    'ep06': [('AScales', [2040, 2055, 2045, 2073, 2090, 2079, 2095, 2079]), ('Scales', [2066, 2068, 2055, 2065, 2078, 2075, 2082, 2075])],
    'ep07': [('AScales', [2031, 2073, 2049, 2013, 2072, 2042, 2045, 2062]), ('Scales', [2058, 2062, 2054, 2059, 2059, 2066, 2073, 2059])],
    'ep08': [('AScales', [2023, 2020, 2051, 2011, 2030, 2032, 2027, 2082]), ('Scales', [2049, 2054, 2058, 2039, 2058, 2059, 2051, 2067])],
    'ep09': [('AScales', [2055, 2051, 2034, 2032, 2100, 2099, 2090, 2077]), ('Scales', [2058, 2057, 2079, 2062, 2063, 2076, 2076, 2072])],
    'ep10x':[('AScales', [2047, 2025, 2063, 2034, 2022, 2054, 2024, 2033]), ('Scales', [2069, 2057, 2062, 2059, 2066, 2070, 2072, 2070])],
    'ep11': [('AScales', [2076, 2067, 2050, 2069, 2083, 2091, 2095, 2081]), ('Scales', [2061, 2052, 2053, 2066, 2053, 2056, 2064, 2080])],
    'ep12': [('AScales', [2039, 2018, 2056, 2049, 2046, 2107, 2076, 2062]), ('Scales', [2062, 2074, 2077, 2051, 2073, 2079, 2076, 2064])],
    'ep13': [('AScales', [2081, 2073, 2087, 2075, 2063, 2123, 2091, 2117]), ('Scales', [2072, 2075, 2072, 2082, 2078, 2072, 2075, 2082])],
    'ep14': [('AScales', [2094, 2107, 2105, 2071, 2070, 2060, 2090, 2083]), ('Scales', [2075, 2071, 2064, 2077, 2066, 2071, 2075, 2081])],
    'ep15x':[('AScales', [2067, 2064, 2059, 2055, 2080, 2047, 2056, 2056]), ('Scales', [2070, 2070, 2076, 2086, 2083, 2074, 2077, 2061])],
    'ep16': [('AScales', [2112, 2095, 2100, 2099, 2089, 2119, 2129, 2154]), ('Scales', [2230, 2253, 2242, 2235, 2229, 2244, 2247, 2249])],
    'ep17': [('AScales', [2129, 2069, 2045, 2103, 2038, 2065, 2121, 2063]), ('Scales', [2239, 2241, 2241, 2233, 2240, 2247, 2260, 2253])],
    'ep18': [('AScales', [2119, 2073, 2111, 2121, 2104, 2097, 2121, 2113]), ('Scales', [2243, 2221, 2254, 2235, 2223, 2256, 2255, 2260])],
}

# -- For recalibration, set everything to defaults:
#PV_SCALES = {
#    name: [('AScales', [2048]*8), ('Scales', [2048]*8)] for name in PV_SCALES   # first step
#    name: [('AScales', [2048]*8), ('Scales', PV_SCALES[name][1][1])] for name in PV_SCALES   # second step
#}

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ('Mode', MODE),  # set to MODE_DIAG for recalibration
    ('Sample1', 0),
    ('AccumulationLength', 30),
    ('NegativeVeto', -16384),
    ('PositiveVeto', 16383),
    ('DiscriminatorLevel', 1024),
    ('BScales', [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ('TubeEnables', [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24),
]

# pixel per tube
PPT_S = 94
PPT_M = 206
PPT_L = 256

# -- For recalibration, set to max. pixel resolution:
#PPT_S = 1024
#PPT_M = 1024
#PPT_L = 1024

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
    'ep09x': [('ModulePixelIdStart', 8*8192),  ('PixelCount', PPT_L)],
    'ep10': [('ModulePixelIdStart', 9*8192),  ('PixelCount', PPT_L)],
    'ep10x': [('ModulePixelIdStart', 9*8192),  ('PixelCount', PPT_L)],
    'ep11': [('ModulePixelIdStart', 10*8192), ('PixelCount', PPT_L)],
    'ep12': [('ModulePixelIdStart', 11*8192), ('PixelCount', PPT_L)],
    'ep13': [('ModulePixelIdStart', 12*8192), ('PixelCount', PPT_M)],
    'ep14': [('ModulePixelIdStart', 13*8192), ('PixelCount', PPT_M)],
    'ep15': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep15x': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep16': [('ModulePixelIdStart', 15*8192), ('PixelCount', PPT_S)],
    'ep17': [('ModulePixelIdStart', 16*8192), ('PixelCount', PPT_S)],
    'ep18': [('ModulePixelIdStart', 17*8192), ('PixelCount', PPT_S)],
}
