
from math import *
from linear import *

def jagged_longedge(a, b, angle, thickness, overhang, overcut):

    indent = thickness/tan(angle)
    extend = thickness/sin(angle) + overhang

    if overcut == 0:
        return replace_line(a, b, tuple( (x/10., y) for x,y in (
            (0,    0),
            (2,    0),
            (2,    -indent),
            (3,    -indent),
            (3,    extend),
            (4,    extend),
            (4,    0),
            (6,    0),
            (6,    -indent),
            (7,    -indent),
            (7,    extend),
            (8,    extend),
            (8,    0),
           #(10,    0),
        ) ) )

    return replace_line(a, b, tuple( (x/10., y) for x,y in (
        (0,    0),
        (2,    0),
        (2,    -indent-overcut),
        (2.15, -indent-overcut),
        (2.15, -indent),
        (2.85, -indent),
        (2.85, -indent-overcut),
        (3,    -indent-overcut),
        (3,    extend),
        (4,    extend),
        (4,    -overcut),
        (4.15, -overcut),
        (4.15, 0),
        (6,    0),
        (6,    -indent-overcut),
        (6.15, -indent-overcut),
        (6.15, -indent),
        (6.85, -indent),
        (6.85, -indent-overcut),
        (7,    -indent-overcut),
        (7,    extend),
        (8,    extend),
        (8,    -overcut),
        (8.15, -overcut),
        (8.15, 0),
       #(10,    0),
    ) ) )

def jagged_shortedge(a, b, angle, thickness, overhang, overcut):

    indent = thickness/tan(angle)
    extend = thickness/sin(angle) + overhang

    if overcut == 0:
        return replace_line(a, b, tuple( (x/7., y) for x,y in (
            (0,    0),
            (1,    0),
            (1,    -indent),
            (2,    -indent),
            (2,    extend),
            (3,    extend),
            (3,    0),
            (4,    0),
            (4,    -indent),
            (5,    -indent),
            (5,    extend),
            (6,    extend),
            (6,    0),
            #(7,    0),
        ) ) )

    return replace_line(a, b, tuple( (x/7., y) for x,y in (
        (0,    0),
        (1,    0),
        (1,    -indent-overcut),
        (1.15, -indent-overcut),
        (1.15, -indent),
        (1.85, -indent),
        (1.85, -indent-overcut),
        (2,    -indent-overcut),
        (2,    extend),
        (3,    extend),
        (3,    -overcut),
        (3.15, -overcut),
        (3.15, 0),
        (4,    0),
        (4,    -indent-overcut),
        (4.15, -indent-overcut),
        (4.15, -indent),
        (4.85, -indent),
        (4.85, -indent-overcut),
        (5,    -indent-overcut),
        (5,    extend),
        (6,    extend),
        (6,    -overcut),
        (6.15, -overcut),
        (6.15, 0),
        #(7,    0),
    ) ) )

def identity(a, b, angle, thickness, overhang, overcut):
    return (a,)

def slot_long(a, b, unit):

    return replace_line(a, b, tuple( (x/10., y) for x,y in (
        (4.8,  -3  *unit),
        (4.8,  -4.2*unit),
        (5.2,  -4.2*unit),
        (5.2,  -3  *unit),
    ) ) )

def slot_short(a, b, unit):

    return replace_line(a, b, tuple( (x/7., y) for x,y in (
        (3.3,  -3  *unit),
        (3.3,  -4.2*unit),
        (3.7,  -4.2*unit),
        (3.7,  -3  *unit),
    ) ) )

def normalize2( (x, y) ):
    d = sqrt(x*x+y*y)
    return (x/d, y/d)

def vector_sub2( (x1,y1), (x2,y2) ):
    return (x1-x2, y1-y2)

def vector_add2( (x1,y1), (x2,y2) ):
    return (x1+x2, y1+y2)

def scalar_mul2( m, (x,y) ):
    return (x*m, y*m)

def interpolate2( (x1,y1), (x2,y2), frac ):
    return ( x2*frac+x1*(1-frac), y2*frac+y1*(1-frac) )

def replace_line(a, b, jag):
    edges = []

    x, y = a
    dx, dy = normalize2(vector_sub2(b, a))
    for l, v in jag:
        edges.append( vector_add2(interpolate2(a, b, l), (-dy*v, dx*v) ) )

    return edges

def purge_doubles(path):
    elems = []
    for a, b in zip(path[1:]+path[:1], path):
        if a != b:
            elems.append(b)
    return elems
        
shape_map = {
    'S' : jagged_shortedge,
    'L' : jagged_longedge,
    'I' : identity,
}

def subdivide(shape, types, angles, thickness, overhang, overcut, shape_map=shape_map):
    edges = []
    for a, b, t, angle in zip(shape, shape[1:]+shape[:1], types, angles):
        edges.append( shape_map[t](a, b, angle, thickness, overhang, overcut))
    return purge_doubles( [ c for e in edges for c in e ] )

slot_map = {
    'S': slot_short,
    'L': slot_long,
}

def slots(shape, types, native_scale, slot_map=slot_map):
    edges = []
    for t, a, b in zip(types, shape, shape[1:]+shape[:1]):
        edges.append( purge_doubles( slot_map[t](a, b, native_scale) ) )

    return tuple( edges )

def cross_product(a, b, c):
    """Cross product AB x AC"""
    ax, ay = a
    bx, by = b
    cx, cy = c
    return (bx-ax) * (cy-ay) - (by-ay) * (cx-ax)

def polygon_crossproduct_sum(poly):
    total = 0
    a = poly[0]
    for i in range(len(poly)-2):
        b,c = poly[i+1:i+3]
        total += cross_product(a, b, c)
    return total

def grow(poly, width):

    points = []

    if polygon_crossproduct_sum(poly) < 0:
        width = -width

    for a, b, c in zip(poly[-1:]+poly[:-1], poly, poly[1:]+poly[:1]):
        ax, ay = a
        bx, by = b
        cx, cy = c
        dx_ab, dy_ab = normalize2( (by-ay, -(bx-ax)) )
        dx_bc, dy_bc = normalize2( (cy-by, -(cx-bx)) )

        mid_x, mid_y = (dx_ab+dx_bc)/2., (dy_ab+dy_bc)/2.
        invdist2 = mid_x*mid_x + mid_y*mid_y

        points.append( (bx+width*mid_x/invdist2, by+width*mid_y/invdist2) )

    return points

