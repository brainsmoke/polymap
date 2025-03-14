
from math import *
from functools import reduce

def d(a, b):
    return sqrt(sum(map(lambda i,j: (i-j)*(i-j), a, b)))

def magnitude( p ):
    x, y, z = p
    return sqrt( x*x + y*y + z*z )

def scalar_product( a, b ):
    x1,y1,z1 = a
    x2,y2,z2 = b

    return x1*x2+y1*y2+z1*z2

def cross_product( a, b ):
    x1,y1,z1 = a
    x2,y2,z2 = b

    return ( y1*z2-y2*z1, z1*x2-z2*x1, x1*y2-x2*y1 )

def vector_add( a, b ):
    x1,y1,z1 = a
    x2,y2,z2 = b

    return (x1+x2, y1+y2, z1+z2)

def vector_sub( a, b ):
    x1,y1,z1 = a
    x2,y2,z2 = b

    return (x1-x2, y1-y2, z1-z2)

def scalar_mul( s, p ):
    x, y, z = p
    return (s*x, s*y, s*z)

def normalize( p ):
    x, y, z = p
    d = sqrt(x*x+y*y+z*z)
    return (x/d, y/d, z/d)

def interpolate( a, b, frac ):
    x1,y1,z1 = a
    x2,y2,z2 = b
    return ( x2*frac+x1*(1-frac), y2*frac+y1*(1-frac), z2*frac+z1*(1-frac) )

def vector_sum( *vecs):
    return reduce( vector_add, vecs )

def norm_add( *vecs ):
    return normalize( vector_sum( *vecs ) )

