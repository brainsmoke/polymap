#
# Copyright (C) 2009 Erik Bosman <ebosman@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a  copy  of  this  software  and  associated  documentation  files
# (the "Software"),  to  deal  in  the  Software  without  restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software
# and to permit  persons to whom  the Software is  furnished to do so,
# subject to the following conditions:
#
# The  above  copyright notice and  this permission notice  shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys, math

import globe, svg

def arc_path(from_, to, center):
    from_x, from_y = from_
    to_x, to_y = to
    cx, cy = center
    r = math.sqrt((cx-to_x)*(cx-to_x)+(cy-to_y)*(cy-to_y))
    sweep = int( (to_x*from_y - from_x*to_y < 0) )
    return "A %f %f 0 0 %d %f %f" % (r, r, sweep, to_x, to_y)

def region_path(r, center=(0.,0.)):

    if r[0][2] == True:
        lines = r[:-1]
        arc = " "+arc_path(r[-1][:2], r[0][:2], center)
    else:
        lines = r
        arc = ""

    return "M "+" L ".join( "%f,%f" % (x,y) for (x,y,_) in lines )+arc+" z "

def regions_path(regions, center=(0.,0.)):
    return '\n'.join( region_path(r, center) for r in regions )

if __name__ == '__main__':

    sea        = "fill:#7777ff;fill-opacity:1"
    land_front = "fill:#ffcc00;fill-opacity:1"
    land_back  = "fill:#333333;fill-opacity:1"

    r = 6371.
    alt = (r+350)/r
    eye = globe.scalar_mul(alt, globe.ll_deg_to_globe_coord( (5.81946, 52.329996) ) )
    north = globe.ll_deg_to_globe_coord( (133.873987, -23.692496) )
#    north = globe.ll_deg_to_globe_coord( (133.873987, -23.692496) )

    m = globe.get_globe()
    front = globe.cone_project(m, eye=eye, north=north, front=True)
    front = [ map(lambda (x,y,vis): (x*200,-y*200, vis), p) for p in front ]

    back = globe.cone_project(m, eye=eye, north=north, front=False)
    back = [ map(lambda (x,y,vis): (x*200,-y*200, vis), p) for p in back ]

    print svg.header(400, 400)
    print '<g transform="translate(200,200)">'
    print svg.circle(200, sea)
    print svg.path( regions_path(back), style=land_back )
    print svg.path( regions_path(front), style=land_front )
    print '</g>'
    print svg.footer()

