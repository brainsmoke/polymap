
from math import *

def d(a, b):
    return sqrt(sum(map(lambda i,j: (i-j)*(i-j), a, b)))

def magnitude(x, y, z):
	return sqrt( x*x + y*y + z*z )

def scalar_product(v1, v2):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    return x1*x2+y1*y2+z1*z2

def cross_product(v1, v2):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    return ( y1*z2-y2*z1, z1*x2-z2*x1, x1*y2-x2*y1 )

def vector_add(v1, v2):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    return (x1+x2, y1+y2, z1+z2)

def vector_sub(v1, v2):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    return (x1-x2, y1-y2, z1-z2)

def scalar_mul(s, v):
    x,y,z = v[0], v[1], v[2]
    return (s*x, s*y, s*z)

def normalize(v):
    x,y,z = v[0], v[1], v[2]
    d = sqrt(x*x+y*y+z*z)
    return (x/d, y/d, z/d)

def interpolate(v1, v2, frac ):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    return ( x2*frac+x1*(1-frac), y2*frac+y1*(1-frac), z2*frac+z1*(1-frac) )

def vector_sum( *vecs):
	return reduce( vector_add, vecs )

def norm_add( *vecs ):
	return normalize( vector_sum( *vecs ) )

