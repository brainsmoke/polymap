
from math import *
from linear import *

def d(a, b):
    return sum(map(lambda i,j: (i-j)*(i-j), a, b))

def d2(a, b):
    ax, ay = a
    bx, by = b
    return (ax-bx)*(ax-bx) + (ay-by)*(ay-by)

def d3(a, b):
    ax, ay, az = a
    bx, by, bz = b
    return (ax-bx)*(ax-bx) + (ay-by)*(ay-by) + (az-bz)*(az-bz)

def safe_acos(a):
    return acos(min(1.0, max(-1.0, a)))

def ll_to_globe_coord(coord):
    a, b = coord
    sa, ca, sb, cb = sin(a), cos(a), sin(b), cos(b)
    x, y, z = sa*cb, sb, ca*cb
    return (x, y, z)

def globe_to_ll_coord(coord):
    x, y, z = coord
    a, b = safe_acos(z/sqrt(1.-y*y)), asin(y) 
    if x < 0:
        a = -a
    return (a, b)

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

def border_node( (x1,y1,z1), (x2,y2,z2), z_border):

    if -0.00001 < z1-z2 < 0.00001:
        frac = .5
    else:
        frac = (z1-z_border)/(z1-z2)

    x, y = (x2*frac+x1*(1-frac)), (y2*frac+y1*(1-frac))
    z = sqrt(x*x+y*y)

    return (x/z, y/z, True)

def internal_node( (x,y,z), factor):
    return (x*factor/-z, y*factor/-z, False)


def inverse_project(globe, eye, center=(0,0,0), north=(0,1,0), front=True):
    center = tuple(map(float, center))
    north  = tuple(map(float, north))
    eye    = tuple(map(float, eye))

    paths = [ look_at(path, eye, center, north) for path in globe ]

    d_center = sqrt(d(center, eye))

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
                if not visible:
                    new_path.append( (last[0]/z, last[1]/z, True ) )

                new_path.append( (v[0]/z, v[1]/z, False) )
                visible = True
            else:
                if visible:
                    new_path.append( (v[0]/z, v[1]/z, True))
                    r.append(new_path)
                    new_path = []

                visible = False

            last = v

        if len(new_path) > 0:
            r.append(new_path)

    return r

def cone_project(globe, eye, center=(0,0,0), north=(0,1,0), front=True):
    center = tuple(map(float, center))
    north  = tuple(map(float, north))
    eye    = tuple(map(float, eye))

    paths = [ look_at(path, eye, center, north) for path in globe ]
    d_center = sqrt(d(center, eye))
    d_cone = d_center - 1./d_center
    factor = sqrt(d_center*d_center - 1.)

    r = []
    for path in paths:

        visible = True
        last = None
        new_path = []

        for i in xrange(len(path)):
            if (d_cone+path[i][2] < 0) == front:
                path = path[i:]+path[:i]+[path[i]]
                visible = False
                break

        for v in path:
            if (d_cone+v[2] >= 0) == front:
                if not visible:
                    new_path.append(border_node(last, v, -d_cone))
            
                new_path.append(internal_node(v, factor))
                visible = True
            else:
                if visible:
                    new_path.append(border_node(last, v, -d_cone))
                    r.append(new_path)
                    new_path = []

                visible = False

            last = v

        if len(new_path) > 0:
            r.append(new_path)

    return r

