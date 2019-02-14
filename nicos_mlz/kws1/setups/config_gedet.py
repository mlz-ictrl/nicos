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
#    ('ep09', 'GE-D7561E-EP'),  # defekt
    ('ep09', 'GE-D71E2C-EP'),
    ('ep10', 'GE-D72EA6-EP'),
    ('ep11', 'GE-D75751-EP'),
    ('ep12', 'GE-D73046-EP'),
    ('ep13', 'GE-D75623-EP'),
    ('ep14', 'GE-D72F44-EP'),
    ('ep15', 'GE-D7304D-EP'),
    ('ep16', 'GE-D74372-EP'),
    ('ep17', 'GE-D7436D-EP'),
    ('ep18', 'GE-D76A50-EP'),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}
# -- To set different HVs for some 8-packs:
# HV_VALUES['ep01'] = 0

PV_SCALES = {
    'ep01': [('AScales', [2207, 2088, 2089, 2105, 2149, 2102, 2105, 2114]), ('Scales', [2247, 2244, 2236, 2250, 2237, 2238, 2216, 2240])],
    'ep02': [('AScales', [2116, 2136, 2160, 2183, 2102, 2134, 2126, 2127]), ('Scales', [2241, 2229, 2243, 2235, 2210, 2213, 2232, 2206])],
    'ep03': [('AScales', [2123, 2116, 2122, 2072, 2093, 2089, 2121, 2102]), ('Scales', [2223, 2234, 2253, 2227, 2225, 2248, 2244, 2233])],
    'ep04': [('AScales', [2136, 2135, 2114, 2083, 2076, 2090, 2093, 2089]), ('Scales', [2055, 2061, 2064, 2057, 2063, 2059, 2049, 2064])],
    'ep05': [('AScales', [2021, 2038, 2076, 2042, 2111, 2097, 2094, 2089]), ('Scales', [2028, 2068, 2055, 2052, 2057, 2082, 2071, 2056])],
    'ep06': [('AScales', [2063, 2068, 2061, 2087, 2112, 2103, 2105, 2083]), ('Scales', [2065, 2069, 2056, 2077, 2070, 2084, 2081, 2079])],
    'ep07': [('AScales', [2059, 2096, 2080, 2044, 2058, 2066, 2088, 2059]), ('Scales', [2046, 2068, 2051, 2068, 2050, 2054, 2053, 2066])],
    'ep08': [('AScales', [2030, 2034, 2053, 2022, 2048, 2054, 2039, 2096]), ('Scales', [2044, 2071, 2054, 2057, 2072, 2064, 2061, 2036])],
    'ep09': [('AScales', [2082, 2074, 2055, 2058, 2120, 2112, 2105, 2094]), ('Scales', [2060, 2057, 2039, 2039, 2052, 2062, 2062, 2066])],
    'ep10': [('AScales', [2083, 2022, 2069, 2052, 2045, 2048, 2044, 2039]), ('Scales', [2077, 2078, 2059, 2061, 2055, 2060, 2034, 2065])],
    'ep11': [('AScales', [2066, 2076, 2052, 2078, 2079, 2090, 2108, 2067]), ('Scales', [2042, 2064, 2045, 2054, 2074, 2061, 2082, 2075])],
    'ep12': [('AScales', [2061, 2034, 2073, 2068, 2062, 2129, 2097, 2070]), ('Scales', [2045, 2057, 2080, 2064, 2071, 2068, 2055, 2066])],
    'ep13': [('AScales', [2096, 2088, 2103, 2086, 2083, 2159, 2097, 2148]), ('Scales', [2058, 2067, 2072, 2078, 2051, 2089, 2075, 2081])],
    'ep14': [('AScales', [2113, 2125, 2136, 2089, 2105, 2096, 2112, 2116]), ('Scales', [2077, 2071, 2084, 2070, 2085, 2087, 2068, 2084])],
    'ep15': [('AScales', [2083, 2145, 2104, 2069, 2105, 2083, 2106, 2109]), ('Scales', [2075, 2090, 2072, 2079, 2062, 2072, 2084, 2067])],
    'ep16': [('AScales', [2173, 2161, 2161, 2168, 2129, 2172, 2189, 2214]), ('Scales', [2239, 2249, 2238, 2242, 2237, 2251, 2247, 2250])],
    'ep17': [('AScales', [2222, 2147, 2121, 2161, 2101, 2135, 2192, 2128]), ('Scales', [2237, 2254, 2248, 2241, 2245, 2239, 2267, 2254])],
    'ep18': [('AScales', [2196, 2144, 2187, 2202, 2178, 2168, 2177, 2186]), ('Scales', [2260, 2225, 2252, 2268, 2237, 2255, 2231, 2268])],
}

# -- For recalibration, set everything to defaults:
#PV_SCALES = {
#    'ep%02d' % i: [('AScales', [2048]*8), ('Scales', PV_SCALES['ep%02d'%i][1][1])] for i in range(1, 19)
#}

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ('Mode', MODE),
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
    'ep14': [('ModulePixelIdStart', 13*8192), ('PixelCount', PPT_M)],
    'ep15': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep16': [('ModulePixelIdStart', 15*8192), ('PixelCount', PPT_S)],
    'ep17': [('ModulePixelIdStart', 16*8192), ('PixelCount', PPT_S)],
    'ep18': [('ModulePixelIdStart', 17*8192), ('PixelCount', PPT_S)],
}
