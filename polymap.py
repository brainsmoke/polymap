#!/usr/bin/env python

import math, sys, os

import globe, svg, pathedit, projection, linear, polymath, maps

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

def get_projection_paths(faces, globe, notches, radius, thickness, overhang, overcut, cutwidth, flip):

    if flip:
        xflip = -1.
    else:
        xflip = 1.

    paths = []
    for i, face in enumerate(faces):
        print "face (%d/%d)" % (i,len(faces))
        eye = face['pos']
        north = face['points'][0]

        edges = [ (xflip*x*radius,-y*radius) for x,y,z in
                projection.look_at(face['points'], eye=eye, north=north) ]

        shape = pathedit.grow(pathedit.subdivide(edges, notches, face['angles'],
                                                 thickness=thickness,
                                                 overhang=overhang,
                                                 overcut=overcut),
                              cutwidth/2.)

        bbox = get_bounding_box(shape)

        proj = projection.inverse_project(globe, eye=eye, north=north, front=True)

        engraving = []
        for p in proj:
            new_path = pathedit.sloppy_bbox_clip( [ (xflip*x*radius,-y*radius) for x,y in p ], bbox )
            if len(new_path) > 3:
                engraving.append(new_path)

        # add dummy box to keep inkscape happy
        if len(engraving) == 0:
            min_x, min_y = bbox[:2]
            engraving = [ [ (min_x-1, min_y), (min_x-1, min_y-1), (min_x, min_y-1), (min_x, min_y) ] ]

        paths.append( { 'bbox'      : bbox,
                        'borders'   : shape,
                        'projection': engraving,
                        'neighbours': face['neighbours'],
                        'points'    : edges } )

    return paths


def inkscape_batch_intersection(filename, face_count, invert):
    argv = [ 'inkscape', filename ]

    if invert:
        action = 'SelectionDiff'
    else:
        action = 'SelectionIntersect'

    for i in xrange(face_count):
        argv += [ '--select=engrave_'+str(i), '--verb', 'SelectionUnGroup', '--verb', action, '--verb', 'EditDeselect' ]

    argv += [ '--verb', 'FileSave', '--verb', 'FileQuit' ]
    os.spawnvp(os.P_WAIT, 'inkscape', argv)

def write_polygon_projection_svg(f, facepaths, sheetwidth, padding, use_numbers, use_map):

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
        borders_path = svg.polygon_path(face['borders'])
        projection_path = svg.polygon_multipath(face['projection'])

        borders = svg.path( borders_path, style=cut )

        if use_map:
            engraving = svg.group( svg.path( borders_path, style=engrave )+
                                   svg.path( projection_path, style=engrave ),
                                   id='engrave_'+str(i) )
        else:
            engraving = ''

        if use_numbers:
            text = svg.text(0,25, str(i), style=comment+';'+textstyle )

            for n, a, b in zip(face['neighbours'],
                               face['points'], face['points'][1:]+face['points'][:1]):
                x1, y1 = a
                x2, y2 = b
                dx, dy = (x1+x2)/3., (y1+y2)/3.+15
                text += svg.text(dx,dy, str(n), style=comment+';'+smalltextstyle )
        else:
            text = ''

        f.write(svg.group( svg.group(borders + engraving) + text, transform='translate('+str(x)+' '+str(y)+')', id='face_'+str(i) ))

    f.write(svg.footer())

def render_polyhedron_map(filename, faces, notches,
                          radius, thickness, overhang, overcut, cutwidth, padding, sheetwidth, flip, invert, use_numbers, map_type):

    if map_type != None:
        g = globe.get_map(maps.map_file(map_type))
    else:
        g = []

    facepaths = get_projection_paths(faces, g, notches=notches,
                                     radius=radius,
                                     thickness=thickness,
                                     overhang=overhang,
                                     overcut=overcut,
                                     cutwidth=cutwidth,
                                     flip=flip)
    f = open(filename, "w")
    write_polygon_projection_svg(f, facepaths, sheetwidth, padding, use_numbers, map_type != None)
    f.close()

    if map_type != None:
        inkscape_batch_intersection(filename, len(faces), invert)

projections = (

    ('T', "Tetrahedron (???)", polymath.tetrahedron_faces, "LLL"),
    ('O', "Octahedron (???)", polymath.octahedron_faces, "LLL"),
    ('C', "Cube (???)", polymath.cube_faces, "LLLL"),
    ('D', "Dodecahedron", polymath.dodecahedron_faces, "LLLLL"),
    ('I', "Icosahedron", polymath.icosahedron_faces, "LLL"),
    ('tT', "Truncated tetrahedron (???)", polymath.truncated_tetrahedron_faces, "LLLLLL"),
    ('tC', "Truncated cube (???)", polymath.truncated_cube_faces, "LLLLLLLL"),
    ('bC', "Truncated cuboctahedron", polymath.truncated_cuboctahedron_faces, "LLLLLLLL"),
    ('tO', "Truncated octahedron (???)", polymath.truncated_octahedron_faces, "LLLLLL"),
    ('tD', "Truncated dodecahedron", polymath.truncated_dodecahedron_faces, "LLLLLLLLLL"),
    ('bD', "Truncated icosidodecahedron", polymath.truncated_icosidodecahedron_faces, "LLLLLLLLLL"),
    ('tI', "Truncated icosahedron", polymath.truncated_icosahedron_faces, "LLLLLL"),
    ('aC', "Cuboctahedron (???)", polymath.cuboctahedron_faces, "LLLL"),
    ('aD', "Icosidodecahedron", polymath.icosidodecahedron_faces, "LLLLL"),
    ('eC', "Rhombicuboctahedron", polymath.rhombicuboctahedron_faces, "LLLL"),
    ('eD', "Rhombicosidodecahedron", polymath.rhombicosidodecahedron_faces, "LLLLL"),
    ('sC', "Snub cube", polymath.snub_cube_faces, "LLLL"),
    ('sD', "Snub dodecahedron", polymath.snub_dodecahedron_faces, "LLLLL"),
    ('kT', "Triakis tetrahedron", polymath.triakis_tetrahedron_faces, "LLL"),
    ('kO', "Triakis octahedron", polymath.triakis_octahedron_faces, "LLL"),
    ('mC', "Disdyakis dodecahedron", polymath.disdyakis_dodecahedron_faces, "LLL"),
    ('kC', "Tetrakis hexahedron", polymath.tetrakis_hexahedron_faces, "LLL"),
    ('kI', "Triakis icosahedron", polymath.triakis_icosahedron_faces, "LLL"),
    ('mD', "Disdyakis triacontahedron", polymath.disdyakis_triacontahedron_faces, "LLL"),
    ('kD', "Pentakis dodecahedron", polymath.pentakis_dodecahedron_faces, "LLL"),
    ('jC', "Rhombic dodecahedron", polymath.rhombic_dodecahedron_faces, "LLLL"),
    ('jD', "Rhombic triacontahedron", polymath.rhombic_triacontahedron_faces, "LLLL"),
    ('oC', "Deltoidal icositetrahedron", polymath.deltoidal_icositetrahedron_faces, "SLLS"),
    ('oD', "Deltoidal hexecontahedron", polymath.deltoidal_hexecontahedron_faces, "SLLS"),
    ('gC', "Pentagonal icositetrahedron", polymath.pentagonal_icositetrahedron_faces, "SSSLL"),
    ('gD', "Pentagonal hexecontahedron", polymath.pentagonal_hexecontahedron_faces, "SSSLL"),

)

if __name__ == '__main__':

    import argparse

    type_choices = [ x[0] for x in projections ]
    map_choices = maps.list_maps()

    epilog = 'Supported solids: \n\n'+\
    '\n'.join("\t"+name+': '+desc for name,desc,_,_ in projections) + '\n\n' +\
    """Errata:

    - Solids marked ??? may have too steep dihedral angles
      (different notches are required)
    - this script invokes inkscape to do a boolean path intersection operation
      this seems to fail for the tC solid (Europe's missing.)

    """

    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("filename", help="output svg", type=str)
    parser.add_argument("--type", help="solid type (Conway name)", choices=type_choices, default='oD')
    parser.add_argument("--map", help="map engraving", choices=map_choices, default='earth')
    parser.add_argument("--radius", help="polyhedron's radius (mm) (default: 100)", type=float, default=100.)
    parser.add_argument("--thickness", help="material thickness (mm) (default: 3.)", type=float, default=3.)
    parser.add_argument("--overhang", help="overhang of notches (mm) (default: .3)", type=float, default=.3)
    parser.add_argument("--overcut", help="overcut in corners to account for cutting width (mm) (default: 0)", type=float, default=0.)
    parser.add_argument("--padding", help="padding between faces (mm) (default: 3.)", type=float, default=3.)
    parser.add_argument("--sheetwidth", help="maximum sheet width (mm) (default: 550)", type=float, default=550.)
    parser.add_argument("--cutwidth", help="cutting width of laser(mm) (default: .15)", type=float, default=.15)
    parser.add_argument("--flip", help="engrave on the backside", action="store_true")
    parser.add_argument("--dpi", help="dpi used for svg, (default: 90, as used by inkscape)", type=float, default=90)
    parser.add_argument("--invert", help="engrave seas instead of landmass", action="store_true")
    parser.add_argument("--nonumbers", help="do not plot number hints", action="store_true")
    parser.add_argument("--noengraving", help="do not plot world map", action="store_true")

    args = parser.parse_args()

    if args.noengraving:
        args.map = None

    #
    # convert to inkscape sizes
    #

    scale = args.dpi/25.4

    for name, _, faces_func, notches in projections:
        if name == args.type:
            break

    faces = faces_func()

    render_polyhedron_map(args.filename, faces, notches,
                          radius=args.radius*scale,
                          thickness=args.thickness*scale,
                          overhang=args.overhang*scale,
                          overcut=args.overcut*scale,
                          cutwidth=args.cutwidth*scale,
                          padding=args.padding*scale,
                          sheetwidth=args.sheetwidth*scale,
                          flip=args.flip,
                          invert=args.invert,
                          use_numbers=not args.nonumbers,
                          map_type=args.map)
