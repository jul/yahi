from yahi.fixed_size_dict import *
from time import time
sample=1000000
def time_for(size, constructor):
    if constructor==dict:
        a=dict()
    else:
        a=constructor(size)
    print "size %d" % size
    print "fact %s" % repr(constructor.__name__)
    start = time()
    for i in xrange(sample):
        a[i]=i
    print "took %f" % (time() - start)
for size in [ 10, 100, 1000, 10000]:
    for constructor in bmFixedLookupTable, FixedLookupTable,dict:
        time_for(size,constructor)
        

a=bmFixedLookupTable(10)
b=FixedLookupTable(10)
for i in xrange(200):
    b[i]=i
    a[i]=i
print a
print b
