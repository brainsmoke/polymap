
from math import *
from linear import *

def matrix_mul(M, v):
    return tuple([ scalar_product(M[row], v) for row in xrange(len(M)) ])

def look_at(path, eye, center=(0,0,0), north=(0,1,0)):
    f     = normalize(vector_sub(center, eye))
    f_neg = normalize(vector_sub(eye, center))
    up = normalize(north)
    s = normalize(cross_product(f, up))
    u = cross_product(s, f)
    M = ( s, u, f_neg )
    return [ matrix_mul(M, vector_sub(v, eye)) for v in path ]

def inverse_project(globe, eye, center=(0,0,0), north=(0,1,0), front=True):
    center = tuple(map(float, center))
    north  = tuple(map(float, north))
    eye    = tuple(map(float, eye))

    paths = [ look_at(path, eye, center, north) for path in globe ]

    d_center = d(center, eye)

    r = []
    for path in paths:

        visible = True
        last = None
        new_path = []

        for i in xrange(len(path)):
            z = path[i][2]+d_center
            if z < .5:
                path = path[i:]+path[:i]+[path[i]]
                visible = False
                break

        for v in path:
            z = v[2]+d_center
            if z >= .5:
                m = d_center/z
                if not visible:
                    new_path.append( (last[0]*m, last[1]*m, True ) )

                new_path.append( (v[0]*m, v[1]*m, False) )
                visible = True
            else:
                if visible:
                    m = d_center/z
                    new_path.append( (v[0]*m, v[1]*m, True))
                    r.append(new_path)
                    new_path = []

                visible = False

            last = v

        if len(new_path) > 0:
            r.append(new_path)

    return r

