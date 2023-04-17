import pkg_resources

VERSION = pkg_resources.require('psutils')[0].version
version_banner=f'''\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
'''

import argparse
import re
import sys
import warnings
from typing import List

from psutils import (
    HelpFormatter, die, parsedimen, setup_input_and_output, simple_warning,
)

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Fit an Encapsulated PostScript file to a given bounding box.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] LLX LLY URX URY [INFILE [OUTFILE]]',
        add_help=False,
    )
    warnings.showwarning = simple_warning(parser.prog)

    parser.add_argument('-c', '--center', '--centre', action='store_true',
                        help='center the image in the given bounding box')
    parser.add_argument('-r', '--rotate', action='store_true',
                        help='rotate the image by 90 degrees counter-clockwise')
    parser.add_argument('-a', '--aspect', action='store_true',
                        help='adjust the aspect ratio to fit the bounding box')
    parser.add_argument('-m', '--maximize', '--maximise', action='store_true',
                        help='rotate the image to fill more of the page if possible')
    parser.add_argument('-s', '--showpage', action='store_true',
                        help='append a /showpage to the file to force printing')
    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('fllx', metavar='LLX', type=parsedimen,
                        help='x coordinate of lower left corner of the box')
    parser.add_argument('flly', metavar='LLX', type=parsedimen,
                        help='y coordinate of lower left corner of the box')
    parser.add_argument('furx', metavar='LLX', type=parsedimen,
                        help='x coordinate of upper right corner of the box')
    parser.add_argument('fury', metavar='LLX', type=parsedimen,
                        help='y coordinate of upper right corner of the box')
    parser.add_argument('infile', metavar='INFILE', nargs='?',
                        help="`-' or no INFILE argument means standard input")
    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        help="`-' or no OUTFILE argument means standard output")
    return parser

def main(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    urx, ury, llx, lly = 0, 0, 0, 0

    infile, outfile = setup_input_and_output(args.infile, args.outfile)

    bbfound = False # %%BoundingBox: found
    for line in infile:
        if re.match(r'%[%!]', line): # still in comment section
            if line.startswith('%%BoundingBox:'):
                m = re.match(r'%%BoundingBox: +([\d.]+) +([\d.]+) +([\d.]+) +([\d.]+)$', line)
                if m:
                    bbfound = True
                    llx = int(m[1]) # accept doubles, but convert to int
                    lly = int(m[2])
                    urx = int(float(m[3]) + 0.5)
                    ury = int(float(m[4]) + 0.5)
            elif line.startswith('%%EndComments'): # don't repeat %%EndComments
                break
            else:
                outfile.write(line)
        else:
            break

    if bbfound == False:
        die('no %%BoundingBox:', 2)

    # Write bounding box, followed by scale & translate
    xoffset, yoffset = args.fllx, args.flly
    width, height = urx - llx, ury - lly

    # FIXME: Consider more carefully how --rotate and --maximize should interact
    rotate = args.rotate
    if args.maximize and \
        (((width > height) and (args.fury - args.flly > args.furx - args.fllx)) or \
        ((width < height) and (args.fury - args.flly < args.furx - args.fllx))):
        rotate = True

    fwidth, fheight = args.furx - args.fllx, args.fury - args.flly
    if rotate:
        fwidth, fheight = fheight, fwidth

    xscale, yscale = fwidth / width, fheight / height

    if not args.aspect: # preserve aspect ratio?
        xscale = yscale = min(xscale, yscale)
    width *= xscale # actual width and height after scaling
    height *= yscale
    if args.center:
        if rotate:
            xoffset += (fheight - height) / 2
            yoffset += (fwidth - width) / 2
        else:
            xoffset += (fwidth - width) / 2
            yoffset += (fheight - height) / 2
    print(f'%%BoundingBox: {int(xoffset)} {int(yoffset)} {int(xoffset + (height if rotate else width))} {int(yoffset + (width if rotate else height))}', file=outfile)
    if rotate: # compensate for original image shift
        xoffset += height + lly * yscale # displacement for rotation
        yoffset -= llx * xscale
    else:
        xoffset -= llx * xscale
        yoffset -= lly * yscale
    print('%%EndComments', file=outfile)
    if args.showpage:
        print('save /showpage{}def /copypage{}def /erasepage{}def', file=outfile)
    else:
        print('%%BeginProcSet: epsffit 1 0', file=outfile)
    print(f'gsave {xoffset:.3f} {yoffset:.3f} translate', file=outfile)
    if rotate:
        print('90 rotate', file=outfile)
    print(f'{xscale:.3f} {yscale:.3f} scale', file=outfile)
    if not args.showpage:
        print('%%EndProcSet', file=outfile)
    outfile.write(infile.read())
    print('grestore', file=outfile)
    if args.showpage:
        print('restore showpage', file=outfile) # just in case


if __name__ == '__main__':
    main()
