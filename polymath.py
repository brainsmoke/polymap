
import math
from linear import normalize, vector_sub, vector_sum, scalar_product, scalar_mul
from linear import cross_product, d, magnitude

def canonical_rotation( v ):
    """ returns (canonical_first_elem, rotated_vector) """
    best = tuple( v )
    best_ix = 0
    for i in range(1, len(v)):
        cur = tuple( v[i:]+v[:i] )
        if (cur < best):
            best = cur
            best_ix = i
    return best_ix, best

def scale_to_plane_on_normal(point, normal):
    return scalar_mul(scalar_product(normal,normal) / scalar_product(point,normal), point)

def find_neighbours(plist, ix):
    min_d = min( d(plist[ix], x) for i,x in enumerate(plist) if i != ix )
    return tuple( i for i,x in enumerate(plist) if min_d-.001 < d(plist[ix], x) < min_d+.001 )

def find_next_point(plist, a, b, c):
    v_in  = vector_sub(plist[b], plist[a])
    v_out = vector_sub(plist[c], plist[b])
    prod = cross_product(v_in, v_out)
    for i in find_neighbours(plist, c):
        v_new = vector_sub(plist[i], plist[c])
        prod_new = cross_product(v_out, v_new)
        if d(prod, prod_new) < 0.001:
            return i

    raise Exception("meh")

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
    nlist = find_neighbours(plist, ix)
    onlist = [ nlist[0] ]
    while len(onlist) < len(nlist):
        n_in = onlist[-1]
        v_in = normalize(vector_sub(p, plist[n_in]))
        min_scalar = None
        next_p = None
        # next_prod = None
        for n_out in nlist:
            if n_in != n_out:
                v_out = normalize(vector_sub(plist[n_out], p))
                sprod = scalar_product(v_in, v_out)
                prod = cross_product(v_in, v_out)
                if scalar_product(p, prod) < 0 and (next_p == None or sprod < min_scalar):
                    min_scalar = sprod
                    next_p = n_out
                    # next_prod = prod
        onlist += [next_p]
    return tuple(onlist)

def dihedral_angle(f1_pos, f2_pos):
    a, b, c = magnitude(*f1_pos), magnitude(*f2_pos), d(f1_pos, f2_pos)
    return math.acos( (a*a + b*b - c*c) / (2*a*b) )

def vertex_info(plist, ix):
    neighbours = ccw_neighbours(plist, ix)
    faces = tuple( find_regular_polygon(plist, neighbours[j], ix, neighbours[j-1])
                   for j in range(len(neighbours)) )
    # order faces / neighbours (counter clockwise) smallest face first
    first, _ = canonical_rotation( tuple( len(x) for x in faces ) )

    neighbours = neighbours[first:] + neighbours[:first]
    faces = faces[first:] + faces[:first]

    return neighbours, faces

def catalan_face(plist, ix):
    neighbours, faces = vertex_info(plist, ix)

    faces_coords = tuple( tuple( plist[i] for i in f ) for f in faces )

    points = tuple( scale_to_plane_on_normal(vector_sum(*f), normalize(plist[ix]))
                    for f in faces_coords )

    angles = tuple( dihedral_angle( plist[ix], plist[neighbour] )
                    for neighbour in neighbours )

    return {
        'normal': normalize(plist[ix]),
        'pos':    normalize(plist[ix]),
        'points': points,
        'neighbours': neighbours,
        'angles': angles,
    }

def dual_faces(plist):
    return tuple( catalan_face(plist, i) for i in range(len(plist)) )

def archimedean_faces(plist):
    face_list = []
    face_points = []
    facemap = {}

    info = tuple( vertex_info(plist, i) for i in range(len(plist)) )

    for _, faces in info:
        for points in faces:
            if points == canonical_rotation(points)[1]:
                facemap[points] = len(face_list)
                face_points.append(points)
                coords = tuple( normalize(plist[i]) for i in points )
                face_list.append( {
                   'normal': normalize(vector_sum(*coords)),
                   'pos': scalar_mul(1./len(coords), vector_sum(*coords)),
                   'points': coords
                } )

    for i, points in enumerate(face_points):

        neighbours = []

        for p, pnext in zip(points, points[1:]+points[:1]):
            _, faces = info[p]
            for f in faces:
                if f[-1] == pnext:
                    neighbours.append( facemap[canonical_rotation(f)[1]] )
                    break

        angles = [ dihedral_angle( face_list[i]['pos'], face_list[n]['pos'] )
                   for n in neighbours ]

        face_list[i]['neighbours'] = tuple( neighbours )
        face_list[i]['angles'] = tuple( angles )

    return tuple( face_list )

#
# permutations
#

def even_perms(x, y, z):
    return [ (x, y, z), (z, x, y), (y, z, x) ]

def all_perms(x, y, z):
    return even_perms(x, y, z) + even_perms(y, x, z)

def sign_perms(x, y, z):
    xset = yset = zset = (-1., 1.)
    if x == 0: xset = (1,)
    if y == 0: yset = (1,)
    if z == 0: zset = (1,)
    return [ (x*sx, y*sy, z*sz) for sx in xset for sy in yset for sz in zset ]

def even_perms_sign( p ):
    return [ ep for sp in sign_perms(*p) for ep in even_perms(*sp) ]

def all_perms_sign( p ):
    return [ ap for sp in sign_perms(*p) for ap in all_perms(*sp) ]

#
# consts
#

phi = (  math.sqrt(5.) + 1. ) / 2.

#
# Platonic solids
#

def tetrahedron_points():
    points = []
    for x in (-1., 1.):
        points.append( (x, 0, -1./ math.sqrt(2.)) )
        points.append( (0, x,  1./ math.sqrt(2.)) )
    return points

def cube_points():
    return sign_perms( (1, 1, 1) )

def icosahedron_points():
    return even_perms_sign( (0, 1, phi) )

# faces

def tetrahedron_faces(): # T
    return dual_faces(tetrahedron_points())

def octahedron_faces(): # O
    return dual_faces(cube_points())

def cube_faces(): # C
    return archimedean_faces(cube_points())

def dodecahedron_faces(): # D
    return dual_faces(icosahedron_points())

def icosahedron_faces(): # I
    return archimedean_faces(icosahedron_points())

#
# Archimedean solids
#

def truncated_tetrahedron_points():
    points = []

    even_minusses = ( ( 3., 1., 1.),
                      ( 3.,-1.,-1.),
                      (-3., 1.,-1.),
                      (-3.,-1., 1.) )

    for x, y, z in even_minusses:
        points += even_perms(x, y, z)

    return points

def truncated_cube_points():
    return even_perms_sign( ( math.sqrt(2.)-1., 1, 1) )

def truncated_cuboctahedron_points():
    return all_perms_sign( (1, 1.+ math.sqrt(2.), 1.+2* math.sqrt(2.)) )

def truncated_octahedron_points():
    return all_perms_sign( (0, 1, 2) )

def truncated_dodecahedron_points():
    return even_perms_sign( (0, 1./phi, 2.+phi) ) + \
           even_perms_sign( (1./phi, phi, 2*phi) ) + \
           even_perms_sign( (phi, 2, phi**2) )

def truncated_icosidodecahedron_points():
    return even_perms_sign( (1/phi, 1/phi, 3+phi) ) + \
           even_perms_sign( (2/phi, phi, 1+2*phi) ) + \
           even_perms_sign( (1/phi, phi**2, -1+3*phi) ) + \
           even_perms_sign( (-1+2*phi, 2, 2+phi) ) + \
           even_perms_sign( (phi, 3, 2*phi) )

def truncated_icosahedron_points():
    return even_perms_sign( (2, 1+2*phi, phi) ) + \
           even_perms_sign( (1, 2+phi, 2*phi) ) + \
           even_perms_sign( (1, 3*phi, 0) )

def cuboctahedron_points():
    return even_perms_sign( (1, 1, 0) )

def icosidodecahedron_points():
    return even_perms_sign( (phi, 0, 0) ) + \
           even_perms_sign( (1/2., phi/2., (1.+phi)/2.) )

def rhombicuboctahedron_points():
    return even_perms_sign( (1, 1, 1+ math.sqrt(2)) )

def rhombicosidodecahedron_points():
    return even_perms_sign( (1, 1, phi**3) ) + \
           even_perms_sign( (phi**2, phi, 2*phi) ) + \
           even_perms_sign( (2+phi, 0, phi**2) )

def snub_cube_points():
    points = []
    xi = ( ( 17.+3.* math.sqrt(33.) )**(1./3.) -
           (-17.+3.* math.sqrt(33.) )**(1./3.) - 1.) / 3.

    even_plusses = ( (-1.,-1.,-1.), (-1., 1., 1.), ( 1.,-1., 1.), ( 1., 1.,-1) )
    coords = ( ( 1., xi, 1./xi),
               (-xi,-1.,-1./xi) )

    for sx, sy, sz in even_plusses:
        for x,y,z in coords:
            points += even_perms(x*sx, y*sy, z*sz)

    return points

def snub_dodecahedron_points():
    points = []

    phi = (  math.sqrt(5.) + 1. ) / 2.
    phi2 = phi**2
    xi = (phi/2.+ math.sqrt(phi-(5./27.))/2.)**(1./3.) + \
        (phi/2.- math.sqrt(phi-(5./27.))/2.)**(1./3.)
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

    for sx, sy, sz in even_plusses:
        for x,y,z in coords:
            points += even_perms(x*sx, y*sy, z*sz)

    return points

# faces

def truncated_tetrahedron_faces(): # tT
    return archimedean_faces(truncated_tetrahedron_points())

def truncated_cube_faces(): # tC
    return archimedean_faces(truncated_cube_points())

def truncated_cuboctahedron_faces(): # bC
    return archimedean_faces(truncated_cuboctahedron_points())

def truncated_octahedron_faces(): # tO
    return archimedean_faces(truncated_octahedron_points())

def truncated_dodecahedron_faces(): # tD
    return archimedean_faces(truncated_dodecahedron_points())

def truncated_icosidodecahedron_faces(): # bD
    return archimedean_faces(truncated_icosidodecahedron_points())

def truncated_icosahedron_faces(): # tI
    return archimedean_faces(truncated_icosahedron_points())

def cuboctahedron_faces(): # aC
    return archimedean_faces(cuboctahedron_points())

def icosidodecahedron_faces(): # aD
    return archimedean_faces(icosidodecahedron_points())

def rhombicuboctahedron_faces(): # eC
    return archimedean_faces(rhombicuboctahedron_points())

def rhombicosidodecahedron_faces(): # eD
    return archimedean_faces(rhombicosidodecahedron_points())

def snub_cube_faces(): # sC
    return archimedean_faces(snub_cube_points())

def snub_dodecahedron_faces(): # sD
    return archimedean_faces(snub_dodecahedron_points())

#
# Catalan solids
#

# faces

def triakis_tetrahedron_faces(): # kT
    return dual_faces(truncated_tetrahedron_points())

def triakis_octahedron_faces(): # kO
    return dual_faces(truncated_cube_points())

def disdyakis_dodecahedron_faces(): # mC
    return dual_faces(truncated_cuboctahedron_points())

def tetrakis_hexahedron_faces(): # kC
    return dual_faces(truncated_octahedron_points())

def triakis_icosahedron_faces(): # kI
    return dual_faces(truncated_dodecahedron_points())

def disdyakis_triacontahedron_faces(): # mD
    return dual_faces(truncated_icosidodecahedron_points())

def pentakis_dodecahedron_faces(): # kD
    return dual_faces(truncated_icosahedron_points())

def rhombic_dodecahedron_faces(): # jC
    return dual_faces(cuboctahedron_points())

def rhombic_triacontahedron_faces(): # jD
    return dual_faces(icosidodecahedron_points())

def deltoidal_icositetrahedron_faces(): # oC
    return dual_faces(rhombicuboctahedron_points())

def deltoidal_hexecontahedron_faces(): # oD
    return dual_faces(rhombicosidodecahedron_points())

def pentagonal_icositetrahedron_faces(): # gC
    return dual_faces(snub_cube_points())

def pentagonal_hexecontahedron_faces(): # gD
    return dual_faces(snub_dodecahedron_points())

