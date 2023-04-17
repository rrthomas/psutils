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
from typing import List, NoReturn, Optional

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import AnnotationBuilder

from psutils import (
    HelpFormatter, die, parsepaper, parsedraw,
    setup_input_and_output, singledimen, simple_warning,
)

# Globals
flipping = False # any spec includes page flip
modulo = 1
scale = 1.0 # global scale factor
rotate = 0 # global rotation

# Command-line parsing helper functions
def specerror() -> NoReturn:
    die('''bad page specification:

  PAGESPECS = [MODULO:]SPEC
  SPEC      = [-]PAGENO[@SCALE][L|R|U|H|V][(XOFF,YOFF)][,SPEC|+SPEC]
              MODULO >= 1; 0 <= PAGENO < MODULO''')

class PageSpec:
    reversed: bool = False
    pageno: int = 0
    rotate: int = 0
    hflip: bool = False
    vflip: bool = False
    scale: float = 1.0
    xoff: float = 0.0
    yoff: float = 0.0

def parsespecs(s: str, width: Optional[float], height: Optional[float]) -> List[List[PageSpec]]:
    global modulo, flipping
    m = re.match(r'(?:([^:]+):)?(.*)', s)
    if not m:
        specerror()
    modulo, specs_text = int(m[1] or '1'), m[2]
    # Split on commas but not inside parentheses.
    pages_text = re.split(r',(?![^()]*\))', specs_text)
    pages = []
    angle = {'l': 90, 'r': -90, 'u': 180}
    for page in pages_text:
        specs = []
        specs_text = page.split('+')
        for spec_text in specs_text:
            m = re.match(r'(-)?(\d+)([LRUHV]+)?(?:@([^()]+))?(?:\((-?[\d.a-z]+),(-?[\d.a-z]+)\))?$', spec_text, re.IGNORECASE | re.ASCII)
            if not m:
                specerror()
            spec = PageSpec()
            if m[1] is not None:
                spec.reversed = True
            if m[2] is not None:
                spec.pageno = int(m[2])
            if m[4] is not None:
                spec.scale = float(m[4])
            if m[5] is not None:
                spec.xoff = singledimen(m[5], width, height)
            if m[6] is not None:
                spec.yoff = singledimen(m[6], width, height)
            if spec.pageno >= modulo:
                specerror()
            if m[3] is not None:
                for mod in m[3]:
                    if re.match(r'[LRU]', mod, re.IGNORECASE):
                        spec.rotate += angle[mod.lower()]
                    elif re.match(r'H', mod, re.IGNORECASE):
                        spec.hflip = not spec.hflip
                    elif re.match(r'V', mod, re.IGNORECASE):
                        spec.vflip = not spec.vflip
            # Normalize rotation and flips
            if spec.hflip and spec.vflip:
                spec.hflip, spec.vflip = False, False
                spec.rotate += 180
            spec.rotate %= 360
            if spec.hflip or spec.vflip:
                flipping = True
            specs.append(spec)
        pages.append(specs)
    return pages

class Range:
    start: int
    end: int
    text: str

def parserange(ranges_text: str) -> List[Range]:
    ranges = []
    for range_text in ranges_text.split(','):
        r = Range()
        if range_text == '_':
            r.start, r.end = 0, 0 # so page_to_real_page() returns -1
        else:
            m = re.match(r'(_?\d+)?(?:(-)(_?\d+))?$', range_text)
            if not m:
                die(f"`{range_text}' is not a page range")
            start = m[1] or '1'
            end = (m[3] or '-1') if m[2] else m[1]
            start = re.sub('^_', '-', start)
            end = re.sub('^_', '-', end)
            r.start, r.end = int(start), int(end)
        r.text = range_text
        ranges.append(r)
    return ranges

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Rearrange pages of a PDF document.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] [INFILE [OUTFILE]]',
        add_help=False,
        epilog='''
PAGES is a comma-separated list of pages and page ranges.

SPECS is a list of page specifications [default is "0", which selects
each page in its normal order].
''',
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument('-S', '--specs', default='0',
                        help='page specifications (see below)')
    parser.add_argument('-R', '--pages', dest='pagerange', type=parserange,
                        help='select the given page ranges')
    parser.add_argument('-e', '--even', action='store_true',
                        help='select even-numbered output pages')
    parser.add_argument('-o', '--odd', action='store_true',
                        help='select odd-numbered output pages')
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='reverse the order of the output pages')
    parser.add_argument('-p', '--paper', type=parsepaper,
                        help='output paper name or dimensions (WIDTHxHEIGHT)')
    parser.add_argument('-P', '--inpaper', type=parsepaper,
                        help='input paper name or dimensions (WIDTHxHEIGHT)')
    parser.add_argument('-d', '--draw', metavar='DIMENSION', nargs='?',
                        type=parsedraw, default=0,
                        help='''\
draw a line of given width (relative to original
page) around each page [argument defaults to 1pt;
default is no line]''')
    parser.add_argument('-q', '--quiet', action='store_false', dest='verbose',
                        help="don't show page numbers being output")
    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('infile', metavar='INFILE', nargs='?',
                        help="`-' or no INFILE argument means standard input")
    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        help="`-' or no OUTFILE argument means standard output")

    return parser

def main(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    global modulo

    args = get_parser().parse_intermixed_args(argv)
    width: Optional[float] = None
    height: Optional[float] = None
    iwidth: Optional[float] = None
    iheight: Optional[float] = None
    if args.paper:
        width, height = args.paper
    if args.inpaper:
        iwidth, iheight = args.inpaper
    specs = parsespecs(args.specs, width, height)

    if (width is None) ^ (height is None):
        die('output page width and height must both be set, or neither')
    if (iwidth is None) ^ (iheight is None):
        die('input page width and height must both be set, or neither')

    infile, outfile = setup_input_and_output(args.infile, args.outfile, True, True)

    pdf = PdfReader(infile)

    if iwidth is None:
        mediabox = pdf.pages[0].mediabox
        iwidth, iheight = mediabox.width, mediabox.height
    if width is None:
        width, height = iwidth, iheight

    # Page spec routines for page rearrangement
    def abs_page(n: int) -> int:
        if n < 0:
            n += len(pdf.pages) + 1
            n = max(n, 1)
        return n

    def page_index_to_page_number(ps: PageSpec, maxpage: int, modulo: int, pagebase: int) -> int:
        return (maxpage - pagebase - modulo if ps.reversed else pagebase) + ps.pageno

    def ps_transform(ps: PageSpec) -> bool:
        return ps.rotate != 0 or ps.hflip or ps.vflip or ps.scale != 1.0 or ps.xoff != 0.0 or ps.yoff != 0.0

    def pdftopdf(in_pdf: PdfReader, pagerange: List[Range], modulo: int, odd: bool, even: bool, reverse: bool, specs: List[List[PageSpec]], draw: bool) -> None:
        out_pdf = PdfWriter()
        outputpage = 0
        # If no page range given, select all pages
        if pagerange is None:
            pagerange = parserange('1-_1')

        # Normalize end-relative pageranges
        for r in pagerange:
            r.start = abs_page(r.start)
            r.end = abs_page(r.end)

        # Get list of pages
        page_list: List[int] = []
        # Returns -1 for an inserted blank page (page number '_')
        def page_to_real_page(p: int) -> int:
            try:
                return page_list[p]
            except IndexError:
                return 0

        for r in pagerange:
            inc = -1 if r.end < r.start else 1
            currentpg = r.start
            while r.end - currentpg != -inc:
                if currentpg > len(in_pdf.pages):
                    die(f"page range {r.text} is invalid", 2)
                if not(odd and (not even) and currentpg % 2 == 0) and not(even and not odd and currentpg % 2 == 1):
                    page_list.append(currentpg - 1)
                currentpg += inc
        pages_to_output = len(page_list)

        # Calculate highest page number output (including any blanks)
        maxpage = pages_to_output + (modulo - pages_to_output % modulo) % modulo

        # Reverse page list if reversing pages
        if reverse:
            page_list.reverse()

        # Rearrange pages
        pagebase = 0
        while pagebase < maxpage:
            for page in specs:
                if args.verbose: # Construct the page label from the input page numbers
                    pagelabels = []
                    for spec in page:
                        n = page_to_real_page(page_index_to_page_number(spec, maxpage, modulo, pagebase))
                        pagelabels.append(str(n + 1) if n >= 0 else '*')
                    pagelabel = ",".join(pagelabels)
                    outputpage += 1
                    sys.stderr.write(f'[{pagelabel}] ')
                page_number = page_index_to_page_number(page[0], maxpage, modulo, pagebase)
                real_page = page_to_real_page(page_number)
                if len(page) == 1 and not ps_transform(page[0]) and page_number < pages_to_output and 0 <= real_page < len(in_pdf.pages) and args.draw == 0:
                    out_pdf.add_page(in_pdf.pages[real_page])
                else:
                    # Add a blank page of the correct size to the end of the document
                    outpdf_page = out_pdf.add_blank_page(width, height)
                    for ps in page:
                        page_number = page_index_to_page_number(ps, maxpage, modulo, pagebase)
                        real_page = page_to_real_page(page_number)
                        if page_number < pages_to_output and 0 <= real_page < len(in_pdf.pages):
                            # Calculate input page transformation
                            t = Transformation()
                            if ps.hflip:
                                assert iwidth is not None
                                t = t.transform(Transformation((-1, 0, 0, 1, iwidth, 0)))
                            elif ps.vflip:
                                assert iheight is not None
                                t = t.transform(Transformation((1, 0, 0, -1, 0, iheight)))
                            if ps.rotate != 0:
                                t = t.rotate((ps.rotate + rotate) % 360)
                            if ps.scale != 1.0:
                                t = t.scale(ps.scale, ps.scale)
                            if ps.xoff is not None:
                                t = t.translate(ps.xoff, ps.yoff)
                            # Merge input page into the output document
                            outpdf_page.merge_transformed_page(in_pdf.pages[real_page], t)
                            if draw > 0: # FIXME: draw the line at the requested width
                                mediabox = in_pdf.pages[real_page].mediabox
                                line = AnnotationBuilder.polyline(
                                    vertices=[
                                        (mediabox.left + ps.xoff, mediabox.bottom + ps.yoff),
                                        (mediabox.left + ps.xoff, mediabox.top + ps.yoff),
                                        (mediabox.right + ps.xoff, mediabox.top + ps.yoff),
                                        (mediabox.right + ps.xoff, mediabox.bottom + ps.yoff),
                                        (mediabox.left + ps.xoff, mediabox.bottom + ps.yoff),
                                    ],
                                )
                                out_pdf.add_annotation(outpdf_page, line)

            pagebase += modulo

        out_pdf.write(outfile)
        if args.verbose:
            print(f'\nWrote {outputpage} pages', file=sys.stderr)

    # Output the pages
    pdftopdf(pdf, args.pagerange, modulo, args.odd, args.even, args.reverse, specs, args.draw)


if __name__ == '__main__':
    main()
