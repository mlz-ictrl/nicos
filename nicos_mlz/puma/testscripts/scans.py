# pylint: skip-file

# Mono lift scan:
for i in range(5):
    mchanger._step('lift', 'top2')
    mchanger._step('lift', 'ref')

# inelastic scan:
for i in range(5):
    qscan((1, 1, 0, 0), (0, 0, 0, 1), 16, kf=2.662, t=1)
    print(i)

for i in range(5):
    qscan((1, 1, 0, 0), (0, 0, 0, 0), 1, kf=2.662, t=1)
    qscan((2, 2, 0, 0), (0, 0, 0, 0), 1, kf=2.662, t=1)
    print(i)
