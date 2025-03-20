
# Polymap

Create laser-cuttable polyhedra

## Dependencies

* inkscape (inkscape is not needed when invoked with --noengraving)

## Usage

```
usage: polymap.py [-h]
                  [--type {T,O,C,D,I,tT,tC,bC,tO,tD,bD,tI,aC,aD,eC,eD,sC,sD,kT,kO,mC,kC,kI,mD,kD,jC,jD,oC,oD,gC,gD}]
                  [--map {spiral16,spiral8,spiral,earth}]
                  [--radius RADIUS] [--thickness THICKNESS]
                  [--overhang OVERHANG] [--overcut OVERCUT]
                  [--padding PADDING] [--sheetwidth SHEETWIDTH]
                  [--cutwidth CUTWIDTH] [--flip] [--invert] [--nonumbers]
                  [--noengraving] [--centerdot] [--slots]
                  filename

positional arguments:
  filename              output svg

options:
  -h, --help            show this help message and exit
  --type {T,O,C,D,I,tT,tC,bC,tO,tD,bD,tI,aC,aD,eC,eD,sC,sD,kT,kO,mC,kC,kI,mD,kD,jC,jD,oC,oD,gC,gD}
                        solid type (Conway name)
  --map {spiral16,spiralx,spiral8,spiral,earth}
                        map engraving
  --radius RADIUS       polyhedron's radius (mm) (default: 100)
  --thickness THICKNESS
                        material thickness (mm) (default: 3.)
  --overhang OVERHANG   overhang of notches (mm) (default: .3)
  --overcut OVERCUT     overcut in corners to account for cutting width (mm)
                        (default: 0)
  --padding PADDING     padding between faces (mm) (default: 3.)
  --sheetwidth SHEETWIDTH
                        maximum sheet width (mm) (default: 550)
  --cutwidth CUTWIDTH   cutting width of laser(mm) (default: .15)
  --flip                engrave on the backside
  --invert              engrave seas instead of landmass
  --nonumbers           do not plot number hints
  --noengraving         do not plot world map
  --centerdot           plot a center dot
  --slots               add slots for zip ties

Supported solids: 

	T: Tetrahedron (???)
	O: Octahedron (???)
	C: Cube (???)
	D: Dodecahedron
	I: Icosahedron
	tT: Truncated tetrahedron (???)
	tC: Truncated cube (???)
	bC: Truncated cuboctahedron
	tO: Truncated octahedron (???)
	tD: Truncated dodecahedron
	bD: Truncated icosidodecahedron
	tI: Truncated icosahedron
	aC: Cuboctahedron (???)
	aD: Icosidodecahedron
	eC: Rhombicuboctahedron
	eD: Rhombicosidodecahedron
	sC: Snub cube
	sD: Snub dodecahedron
	kT: Triakis tetrahedron
	kO: Triakis octahedron
	mC: Disdyakis dodecahedron
	kC: Tetrakis hexahedron
	kI: Triakis icosahedron
	mD: Disdyakis triacontahedron
	kD: Pentakis dodecahedron
	jC: Rhombic dodecahedron
	jD: Rhombic triacontahedron
	oC: Deltoidal icositetrahedron
	oD: Deltoidal hexecontahedron
	gC: Pentagonal icositetrahedron
	gD: Pentagonal hexecontahedron

Errata:

    - Solids marked ??? may have too steep dihedral angles
      (different notches are required)
    - this script invokes inkscape to do a boolean path intersection operation
      this seems to fail for the tC solid (Europe's missing.)
```
