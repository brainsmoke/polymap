
import math

def squared_distance(a, b):
    ax, ay, az = a
    bx, by, bz = b
    return (ax-bx)*(ax-bx) + (ay-by)*(ay-by) + (az-bz)*(az-bz)

def safe_acos(a):
    return math.acos(min(1.0, max(-1.0, a)))

def ll_to_globe_coord(coord):
    a, b = coord
    sa, ca, sb, cb = math.sin(a), math.cos(a), math.sin(b), math.cos(b)
    x, y, z = sa*cb, sb, ca*cb
    return (x, y, z)

def globe_to_ll_coord(coord):
    x, y, z = coord
    a, b = safe_acos(z / math.sqrt(1.-y*y)), math.asin(y)
    if x < 0:
        a = -a
    return (a, b)

def mercator_to_globe(m):
    return [ map(ll_to_globe_coord, p) for p in m ]

def globe_to_mercator(m):
    return [ map(globe_to_ll_coord, p) for p in m ]

def join_adjacent(r, dist, max_join=20):

    r = r[:]
    diffs = []

    path = [ i/2                 for i in range(len(r)*2) ]
    side = [ -(i%2)              for i in range(len(r)*2) ]
    end  = [ i+1-2*(i%2)         for i in range(len(r)*2) ]
    loc  = [ r[path[i]][side[i]] for i in range(len(r)*2) ]

    for a in range(len(path)):
        for b in range(a+1, len(path)):
            diff = dist(loc[a], loc[b])
            if diff <= max_join:
                diffs.append( ( diff, a, b ) )

    diffs.sort()

    for (diff, a, b) in diffs:
        first, last = end[a], end[b]

        if first and last:
            end[a] = end[b] = None

            if b == first:
                continue

            if side[a] == side[b]:
                r[path[b]].reverse()

            if side[a] == 0:
                r[path[a]] = r[path[b]]+r[path[a]]
            else:
                r[path[a]] = r[path[a]]+r[path[b]]

            r[path[b]] = None

            end[first], end[last] = last, first
            path[last], side[last] = path[a], side[a]

    return filter(None, r)

def get_regions(filename):
    regions = []
    r = []

    for line in open(filename).readlines():
        if line[0] == '#':
            r = []
            regions.append(r)
        else:
            r.append(tuple(map(lambda x: math.radians(float(x)), line.split("\t"))))

    return regions

def get_globe():
    return join_adjacent(mercator_to_globe(get_regions("data/24577.dat")), dist=squared_distance)

def get_map(filename):
    regions = []
    for r in open(filename).readlines():
        regions.append(tuple(tuple(float(x) for x in p.split(',')) for p in r.split('|')))

    return tuple(regions)

def get_globe_cached():
    return get_map("maps/earth.paths")

def look_at(path, eye, center=(0,0,0), north=(0,1,0)):
    f     = normalize(vector_sub(center, eye))
    f_neg = normalize(vector_sub(eye, center))
    up = normalize(north)
    s = normalize(cross_product(f, up))
    u = cross_product(s, f)
    M = ( s, u, f_neg )
    return [ matrix_mul(M, vector_sub(v, eye)) for v in path ]

def border_node(coord1, coord2, z_border):
    x1, y1, z1 = coord1[0], coord1[1], coord1[2]
    x2, y2, z2 = coord2[0], coord2[1], coord2[2]

    if -0.00001 < z1-z2 < 0.00001:
        frac = .5
    else:
        frac = (z1-z_border)/(z1-z2)

    x, y = (x2*frac+x1*(1-frac)), (y2*frac+y1*(1-frac))
    z = sqrt(x*x+y*y)

    return (x/z, y/z, True)

def internal_node(v, factor):
    x,y,z = v[0], v[1], v[2]
    return (x*factor/-z, y*factor/-z, False)

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

        for i in range(len(path)):
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

