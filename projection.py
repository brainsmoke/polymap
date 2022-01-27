
from linear import scalar_product, normalize, cross_product, vector_sub, d

def matrix_mul(M, v):
    return tuple([ scalar_product(M[row], v) for row in range(len(M)) ])

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

        visible = False
        new_path = []

        for v in path:

            x, y, z = v
            z = z + d_center

#            if z <= 0.:
#                d_underest = ( abs(x)+abs(y) ) / 2.
#                if d_underest > 0.:
#                    #assumed to be pruned in bbox phase
#                    new_path.append( (x/d_underest, y/d_underest) )
#            else:
            if z > 0.:
                m = d_center/z
                x, y = x*m, y*m
                if x*x + y*y < 1.:
                    visible = True

                new_path.append( (x, y) )

        if visible and len(new_path) > 3:
            r.append(new_path)

    return r

