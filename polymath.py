
from math import *
from linear import *

def scale_to_plane_on_normal(point, normal):
    return scalar_mul(scalar_product(normal,normal) / scalar_product(point,normal), point)

def neighbours(plist, ix):
    min_d = min( d(plist[ix], x) for i,x in enumerate(plist) if i != ix )
    return tuple( i for i,x in enumerate(plist) if min_d-.001 < d(plist[ix], x) < min_d+.001 )

def find_next_point(plist, a, b, c):
    v_in  = vector_sub(plist[b], plist[a])
    v_out = vector_sub(plist[c], plist[b])
    prod = cross_product(v_in, v_out)
    for i in neighbours(plist, c):
        v_new = vector_sub(plist[i], plist[c])
        prod_new = cross_product(v_out, v_new)
        if d(prod, prod_new) < 0.001:
            return i

    raise Error("meh")

def find_regular_polygon(plist, last, first, second):
    a, b, c = last, first, second
    poly = [b, c]
    while True:
        a, b, c = b, c, find_next_point(plist, a, b, c)
        poly += [c]
        if c == last:
            return tuple(poly)

def ccw_neighbours(plist, ix):
    p = plist[ix]
    nlist = neighbours(plist, ix)
    onlist = [ nlist[0] ]
    while len(onlist) < len(nlist):
        n_in = onlist[-1]
        v_in = normalize(vector_sub(p, plist[n_in]))
        min_scalar = None
        next_p = None
        next_prod = None
        for n_out in nlist:
            if n_in != n_out:
                v_out = normalize(vector_sub(plist[n_out], p))
                sprod = scalar_product(v_in, v_out)
                prod = cross_product(v_in, v_out)
                if scalar_product(p, prod) < 0 and (next_p == None or sprod < min_scalar):
                    min_scalar = sprod
                    next_p = n_out
                    next_prod = prod
        onlist += [next_p]
    return tuple(onlist)

def dual_dihedral_angle(dual_v1, dual_v2):
    e = d(dual_v1, dual_v2)
    r = magnitude(dual_v1)
    a, b, c = r, r, e
    return acos( (a*a + b*b - c*c) / (2*a*b) )

def catalan_face(dual_point, dual_faces):
    return tuple( scale_to_plane_on_normal(vector_sum(*f), normalize(dual_point)) for f in dual_faces )

def oriented_catalan_face(plist, ix):
    nlist = ccw_neighbours(plist, ix)
    faces = tuple( find_regular_polygon(plist, nlist[j-1], ix, nlist[j]) for j in xrange(len(nlist)) )
    best = tuple( len(x) for x in faces )
    best_ix = 0
    for j in xrange(1, len(nlist)):
        cur = tuple( len(x) for x in faces[j:]+faces[:j] )
        if (cur < best):
            best = cur
            best_ix = j
    nlist = nlist[best_ix:] + nlist[:best_ix]
    faces = faces[best_ix:] + faces[:best_ix]
    points = catalan_face(plist[ix], tuple( tuple( plist[n] for n in f ) for f in faces ) )
    angles = [ dual_dihedral_angle( plist[ix], plist[neighbour] )
               for neighbour in nlist ]

    return {
        'normal': normalize(plist[ix]),
        'pos':    normalize(plist[ix]),
        'points': points,
        'neighbours': nlist,
        'angles': angles,
    }

def dual_faces(plist):
    return tuple( oriented_catalan_face(plist, i) for i in xrange(len(plist)) )

def rhombicosidodecahedron_points():

    points = []
    phi = ( sqrt(5.) + 1. ) / 2.
    phi2 = phi**2
    phi3 = phi**3

    for x in (-1, 1):
        for y in (-1, 1):
            for z in (-phi3, phi3):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-phi2, phi2):
        for y in (-phi, phi):
            for z in (-2*phi, 2*phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-2-phi, 2+phi):
        for z in (-phi2, phi2):
            points.append( (x, 0, z) )
            points.append( (z, x, 0) )
            points.append( (0, z, x) )

    return points

def deltoidal_hexecontahedron_faces():
    return dual_faces(rhombicosidodecahedron_points())

def icosidodecahedron_points():

    points = []
    phi = ( sqrt(5.) + 1. ) / 2.
    phi2 = phi**2
    phi3 = phi**3

    for x in (-phi, phi):
        points.append( (x, 0, 0) )
        points.append( (0, x, 0) )
        points.append( (0, 0, x) )

    for x in (-.5, .5):
        for y in (-phi/2., phi/2.):
            for z in (-(1+phi)/2., (1+phi)/2.):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    return points

def rhombic_triacontahedron_faces():
    return dual_faces(icosidodecahedron_points())


def tetraedron_points():
    points = []
    for x in (-1., 1.):
        points.append( (x, 0, -1./sqrt(2.)) )
        points.append( (0, x,  1./sqrt(2.)) )
    return points

def tetraedron_faces():
    return dual_faces(tetraedron_points())


def truncated_icosidodecahedron_points():

    points = []
    phi = ( sqrt(5.) + 1. ) / 2.
    phi2 = phi**2

    for x in (-1/phi, 1/phi):
        for y in (-1/phi, 1/phi):
            for z in (-3-phi, 3+phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-2/phi, 2/phi):
        for y in (-phi, phi):
            for z in (-1-2*phi, 1+2*phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-1/phi, 1/phi):
        for y in (-phi2, phi2):
            for z in (1-3*phi, -1+3*phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (1-2*phi, -1+2*phi):
        for y in (-2, 2):
            for z in (-2-phi, 2+phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-phi, phi):
        for y in (-3, 3):
            for z in (-2*phi, 2*phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    return points

def disdyakis_triacontahedron_faces():
    return dual_faces(truncated_icosidodecahedron_points())


def snub_dodecahedron_points():
    points = []

    phi = ( sqrt(5.) + 1. ) / 2.
    phi2 = phi**2
    xi = (phi/2.+sqrt(phi-(5./27.))/2.)**(1./3.) + \
        (phi/2.-sqrt(phi-(5./27.))/2.)**(1./3.)
    a = xi - 1/xi
    b = xi*phi + phi2 + phi/xi

    even_plusses = ( (-1.,-1.,-1.), (-1., 1., 1.), ( 1.,-1., 1.), ( 1., 1.,-1) )
    coords = (
        (2*a, 2., 2*b),
        ((a + b/phi + phi), (-a*phi + b + 1/phi), (a/phi + b*phi - 1)),
        ((-a/phi + b*phi + 1), (-a + b/phi - phi), (a*phi + b - 1/phi)),
        ((-a/phi + b*phi - 1), ( a - b/phi - phi), (a*phi + b + 1/phi)),
        ((a + b/phi - phi), (a*phi - b + 1/phi), (a/phi + b*phi + 1)),
    )

    for mx, my, mz in even_plusses:
        for ax,ay,az in coords:
            x, y, z = mx*ax, my*ay, mz*az
            points.append( (x, y, z) )
            points.append( (z, x, y) )
            points.append( (y, z, x) )

    return points

def pentagonal_hexecontahedron_faces():
    return dual_faces(snub_dodecahedron_points())

def cube_points():
    points = []

    for x in (-1., 1):
        for y in (-1., 1):
            for z in (-1., 1):
                points.append( (x, y, z) )

    return points

def octahedron_faces():
    return dual_faces(cube_points())

def rhombicuboctahedron_points():
    points = []

    for x in (-1., 1):
        for y in (-1., 1):
            for z in (-1.-sqrt(2), 1+sqrt(2)):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    return points

def deltoidal_icositetrahedron_faces():
    return dual_faces(rhombicuboctahedron_points())


def snub_cube_points():
    points = []
    xi = ( ( 17.+3.*sqrt(33.) )**(1./3.) -
           (-17.+3.*sqrt(33.) )**(1./3.) - 1.) / 3.

    even_plusses = ( (-1.,-1.,-1.), (-1., 1., 1.), ( 1.,-1., 1.), ( 1., 1.,-1) )
    coords = ( ( 1., xi, 1./xi),
               (-xi,-1.,-1./xi) )

    for mx, my, mz in even_plusses:
        for ax,ay,az in coords:
            x, y, z = mx*ax, my*ay, mz*az
            points.append( (x, y, z) )
            points.append( (z, x, y) )
            points.append( (y, z, x) )

    return points

def pentagonal_icositetrahedron_faces():
    return dual_faces(snub_cube_points())

def truncated_icosahedron_points():
    points = []
    phi = ( sqrt(5.) + 1. ) / 2.

    for x in (-2., 2.):
        for y in (-1-2*phi, 1+2*phi):
            for z in (-phi, phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-1., 1.):
        for y in (-2-phi, 2+phi):
            for z in (-2*phi, 2*phi):
                points.append( (x, y, z) )
                points.append( (z, x, y) )
                points.append( (y, z, x) )

    for x in (-1., 1.):
        for y in (-3.*phi, 3*phi):
            points.append( (x, y, 0) )
            points.append( (0, x, y) )
            points.append( (y, 0, x) )

    return points

def pentakis_dodecahedron_faces():
    return dual_faces(truncated_icosahedron_points())
