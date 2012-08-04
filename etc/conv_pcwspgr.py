f = open('PCWSPGR.DAT')

sg_by_num = {}
sg_by_hm  = {}

f = iter(f)
for line in f:
    if line.startswith('spgr'):
        sp = line.split(None, 8)
        spnum = int(sp[1])
        spvar = int(sp[2])
        sp_hm = sp[8].replace(' ', '').strip()
        sp_cond = f.next()
        conditions = [int(sp_cond[2*i:2*i+2]) for i in range(14)]
        if sp_hm in sg_by_hm:
            if sp_hm not in ('R3', 'R-3', 'R32', 'R3m', 'R3c', 'R-32m', 'R-32/m', 'R-32/c'):
                assert sg_by_num[sg_by_hm[sp_hm]] == conditions, sp_hm
        sg_by_hm[sp_hm] = spnum, spvar
        sg_by_num[spnum, spvar] = conditions

print 'sg_by_num = {'
for k in sorted(sg_by_num):
    print ' %-9s: %s,' % (k, sg_by_num[k])
print '}\n'
print 'sg_by_hm = {'
for k in sorted(sg_by_hm):
    print ' %-9r: %s,' % (k, sg_by_hm[k])
print '}'
