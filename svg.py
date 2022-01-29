
def header(width, height):
    return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   width="""+"\""+str(width)+"mm\""+"""
   height="""+"\""+str(height)+"mm\""+"""
   viewBox=\"0 0 """+str(width)+' '+str(height)+"""\"
   id="dhxdron"
   >"""


def background(width, height, style):
    return "<rect width=\""+str(width)+"\" height=\""+str(height)+"\"" + \
           " style=\""+style+"\" />"


def circle(radius, style):
    return "  <circle r=\""+str(radius)+"\""+" style=\""+style+"\" />\n"


def footer():
    return "</svg>"


def group(code, transform=None, id=None):
    if id:
        ident = ' id="'+id+'"'
    else:
        ident = ''

    if transform:
        trans = ' transform="'+transform+'"'
    else:
        trans = ''

    return "<g"+ident+trans+">"+code+"</g>\n"


def path(path, style=None):
    s = ''
    if style:
        s = ' style="'+style+'"'
    return '<path d="'+path+'"'+s+'/>'


def polygon_path(coords):
    return 'M'+' L'.join(str(x) + ' ' + str(y) for x, y in coords) + ' Z'


def polygon_multipath(paths):
    return '\n'.join(polygon_path(coords) for coords in paths)


def text(x, y, text, id=None, transform=None, style=None):
    t = s = i = ''

    if id:
        i = ' id="' + id + '"'

    if transform:
        t = ' transform="' + transform + '"'

    if style:
        s = ' style="' + style + '"'

    return '<text x="' + str(x) + '" y="' + str(y) + '"' + i + t + s + '>' + \
        text + '</text>'


def use(id, transform=None, style=None):
    t = s = ''

    if transform:
        t = ' transform="' + transform + '"'

    if style:
        s = ' style="' + style + '"'

    return '<use xlink:href="#' + id + '" ' + t + s + '/>'
