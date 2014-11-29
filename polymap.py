#!/usr/bin/env python

import math, sys, os

import globe, svg, pathedit, render, projection, linear, polymath

#
# settings
#

engrave = 'stroke:none;fill:#000000'
clip = 'stroke:none;fill:#0000ff'
cut = 'stroke:#ff0000;fill:none'

comment = 'stroke:none;fill:#0000ff'
textstyle= 'font-size:50px;text-align:center;text-anchor:middle;'
smalltextstyle= 'font-size:30px;text-align:center;text-anchor:middle;'

def get_bounding_box(path):
    """ returns (min_x, min_y, max_x, max_y) """
    if len(path) == 0:
        return 0.,0.,0.,0.

    min_x, min_y = path[0]
    max_x, max_y = path[0]

    for x,y in path[1:]:
        min_x, min_y = min(min_x, x), min(min_y, y)
        max_x, max_y = max(max_x, x), max(max_y, y)

    return (min_x, min_y, max_x, max_y)

def get_projection_paths(faces, globe, nodges, radius, thickness, overhang, overcut, cutwidth, flip):

    if flip:
        xflip = -1.
    else:
        xflip = 1.

    paths = []
    for i, face in enumerate(faces):
        eye = face['pos']
        north = face['points'][0]

        proj = projection.inverse_project(globe, eye=eye, north=north, front=True)
        engraving = [ [ (xflip*x*radius,-y*radius, vis) for x,y,vis in p ]
                      for p in proj if len(p) > 2 ]

        edges = [ (xflip*x*radius,-y*radius) for x,y,z in
                projection.look_at(face['points'], eye=eye, north=north) ]

        shape = pathedit.grow(pathedit.subdivide(edges, nodges, face['angles'],
                                                 thickness=thickness,
                                                 overhang=overhang,
                                                 overcut=overcut),
                              cutwidth/2.)

        paths.append( { 'bbox'      : get_bounding_box(shape),
                        'borders'   : svg.polygon_path(shape),
                        'projection': render.regions_path(engraving),
                        'neighbours': face['neighbours'],
                        'points'    : edges } )

    return paths


def inkscape_batch_intersection(filename, face_count, inverted):
    argv = [ 'inkscape', filename ]

    for i in xrange(face_count):
        if i in inverted:
            action = 'SelectionDiff'
        else:
            action = 'SelectionIntersect'

        argv += [ '--select=engrave_'+str(i), '--verb', 'SelectionUnGroup', '--verb', action, '--verb', 'EditDeselect' ]

    argv += [ '--verb', 'FileSave', '--verb', 'FileQuit' ]
    os.spawnvp(os.P_WAIT, 'inkscape', argv)

def write_polygon_projection_svg(f, facepaths, sheetwidth, padding):

    x, y = padding, padding
    w, cur_h = 0., 0.
    pos = []
    for i, face in enumerate(facepaths):
        min_x, min_y, max_x, max_y = face['bbox']
        face_w, face_h = max_x-min_x, max_y-min_y
        if x + face_w > sheetwidth:
            y += cur_h + padding
            x, cur_h = padding, 0.

        pos.append( (x-min_x, y-min_y) )
        cur_h = max(cur_h, face_h)
        x += face_w + padding
        w = max(w, x)

    h = y + cur_h + padding

    f.write(svg.header(w,h))

    for i, face in enumerate(facepaths):

        x, y = pos[i]
        borders = svg.path( face['borders'], style=cut )
        engraving = svg.group( svg.path( face['borders'], style=engrave )+
                               svg.path( face['projection'], style=engrave ),
                               id='engrave_'+str(i) )
        f.write(svg.group( borders + engraving, transform='translate('+str(x)+' '+str(y)+')' ))

    for i, face in enumerate(facepaths):
        x, y = pos[i]
        s = svg.text(0,25, str(i), style=comment+';'+textstyle )
        for n, a, b in zip(face['neighbours'],
                           face['points'], face['points'][1:]+face['points'][:1]):
            x1, y1 = a
            x2, y2 = b
            dx, dy = (x1+x2)/3., (y1+y2)/3.+15
            s += svg.text(dx,dy, str(n), style=comment+';'+smalltextstyle )

        f.write(svg.group( s, transform='translate('+str(x)+' '+str(y)+')' ))

    f.write(svg.footer())

def render_polyhedron_map(filename, faces, inverted, nodges,
                          radius, thickness, overhang, overcut, cutwidth, padding, sheetwidth, flip):

    g = globe.get_globe_cached()
    facepaths = get_projection_paths(faces, g, nodges=nodges,
                                     radius=radius,
                                     thickness=thickness,
                                     overhang=overhang,
                                     overcut=overcut,
                                     cutwidth=cutwidth,
                                     flip=flip)
    f = open(filename, "w")
    write_polygon_projection_svg(f, facepaths, sheetwidth, padding)
    f.close()

    inkscape_batch_intersection(filename, len(faces), inverted)


#
# Sadly, some tiles have to me manually inverted
#
dhxdron_inverted = (13, 19, 43, 47, 46)
rhombictriacontahedron_inverted = (28,)

projections = {
    'oD' : ("Deltoidal hexecontahedron",  polymath.deltoidalhexecontahedron_faces, dhxdron_inverted, "SLLS"),
    'jD' : ("Rhombic triacontahedron",    polymath.rhombictriacontahedron_faces, rhombictriacontahedron_inverted, "LLLL"),
    'gD' : ("Pentagonal hexecontahedron", polymath.pentagonal_hexecontahedron_faces, (), "SSSLL"),
    'mD' : ("Disdyakis triacontahedron",  polymath.disdyakis_triacontahedron_faces, (), "LLL"),
}

if __name__ == '__main__':

    import argparse

    type_choices = projections.keys()
    type_choices.sort()

    epilog = "Supported solids:\n\n" + '\n'.join("\t"+k+': '+projections[k][0] for k in type_choices) + '\n '

    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("filename", help="output svg", type=str)
    parser.add_argument("--type", help="solid type (Conway name)", choices=type_choices, default='oD')
    parser.add_argument("--radius", help="polyhedron's radius (mm) (default: 100)", type=float, default=100.)
    parser.add_argument("--thickness", help="material thickness (mm) (default: 3.)", type=float, default=3.)
    parser.add_argument("--overhang", help="overhang of nodges (mm) (default: .3)", type=float, default=.3)
    parser.add_argument("--overcut", help="overcut in corners to account for cutting width (mm) (default: 0)", type=float, default=0.)
    parser.add_argument("--padding", help="padding between faces (mm) (default: 3.)", type=float, default=3.)
    parser.add_argument("--sheetwidth", help="maximum sheet width (mm) (default: 550)", type=float, default=550.)
    parser.add_argument("--cutwidth", help="cutting width of laser(mm) (default: .15)", type=float, default=.15)
    parser.add_argument("--flip", help="engrave on the backside", action="store_true")
    parser.add_argument("--dpi", help="dpi used for svg, (default: 90, as used by inkscape)", type=float, default=90)
    parser.add_argument("--invert", help="engrave seas instead of landmass", action="store_true")

    args = parser.parse_args()

    #
    # convert to inkscape sizes
    #

    scale = args.dpi/25.4

    _, faces_func, inverted, nodges = projections[args.type]

    faces = faces_func()

    if args.invert:
        inverted = tuple( x for x in xrange(len(faces)) if x not in inverted )

    render_polyhedron_map(args.filename, faces, inverted, nodges,
                          radius=args.radius*scale,
                          thickness=args.thickness*scale,
                          overhang=args.overhang*scale,
                          overcut=args.overcut*scale,
                          cutwidth=args.cutwidth*scale,
                          padding=args.padding*scale,
                          sheetwidth=args.sheetwidth*scale,
                          flip=args.flip)
