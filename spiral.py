import globe, linear

import math, cmath

delta = 1.
n_rotations = 1
steps_per_rotation = 1000
n_spirals = 16

def spiral(base, n_rotations, steps_per_rotation, delta):

    s = []
    n_steps = n_rotations * steps_per_rotation

    for i in xrange(-n_steps/2, (1+n_steps)/2):
    	c = cmath.rect(1., base+i*math.pi*2/steps_per_rotation)
        x, z = c.real, c.imag
        y = i*math.pi*2/steps_per_rotation*delta
        s.append( linear.normalize( (x, y, z) ) )

    return s

paths = []

for i in range(n_spirals):
    up = spiral(i*math.pi*2 / n_spirals, n_rotations, steps_per_rotation, delta)
    down = spiral((i+.5)*math.pi*2 / n_spirals, n_rotations, steps_per_rotation, delta)
    down.reverse()
    paths += [ up + down ]

for path in paths:
    print '|'.join( "%.16f,%.16f,%.16f" % p for p in path)
