import importlib.metadata

VERSION = importlib.metadata.version('psutils')

version_banner=f'''\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
'''

import argparse
import os
import re
import sys
import warnings
from typing import List

from pypdf import PdfReader, PdfWriter
import puremagic # type: ignore

from psutils import HelpFormatter, die, simple_warning

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Concatenate PDF or PostScript documents.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] FILE...',
        add_help=False,
        epilog='''
The --save and --nostrip options only apply to PostScript files.
''',
)
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument('-e', '--even', action='store_true',
                        help='force each file to an even number of pages')
    parser.add_argument('-s', '--save', action='store_true',
                        help='try to close unclosed save operators')
    parser.add_argument('-n', '--nostrip', action='store_true',
                        help='do not strip prolog or trailer from input files')
    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('file', metavar='FILE', nargs='+',
                        help="`-' or no FILE argument means standard input")

    return parser

def join_pdf(args: argparse.Namespace) -> None:
    # Merge input files
    out_pdf = PdfWriter()
    for file in args.file:
        in_pdf = PdfReader(file)
        out_pdf.append(in_pdf)
        if args.even and len(in_pdf.pages) % 2 == 1:
            out_pdf.add_blank_page()

    # Write output
    out_pdf.write(sys.stdout.buffer)
    sys.stdout.buffer.flush()

def join_ps(args: argparse.Namespace) -> None:
    save = 'save %psjoin\n'
    restore = 'restore %psjoin\n'

    if args.save:
        save = '/#psjoin-save# save def %psjoin\n'
        restore = '#psjoin-save# restore %psjoin\n'

    prolog, prolog_inx, trailer, comments, pages = {}, None, {}, {}, {}
    if args.nostrip:
        prolog_inx = -1
        prolog[prolog_inx] = "% psjoin: don't strip\n"
        trailer[prolog_inx] = "% psjoin: don't strip\n"
        comments[prolog_inx] = ''
    else:
        for i, file in enumerate(args.file):
            try:
                fh = open(file)
            except IOError as e:
                die(f"can't open file `{file}': {e}")

            in_comment = True
            in_prolog = True
            in_trailer = False
            comments[i] = ''
            prolog[i] = ''
            trailer[i] = ''
            pages[i] = 0
            for line in fh:
                if line.startswith('%%BeginDocument'):
                    while not fh.readline().startswith('%%EndDocument'):
                        pass

                if in_comment:
                    if line.startswith('%!PS-Adobe-') or line.startswith('%%Title') or \
                    line.startswith('%%Pages') or line.startswith('%%Creator'):
                        continue
                    if line.startswith('%%EndComments'):
                        in_comment = False
                    comments[i] += line
                    continue
                if in_prolog:
                    if line.startswith('%%Page:'):
                        in_prolog = False
                    else:
                        prolog[i] += line
                        continue

                if line.startswith('%%Trailer'):
                    in_trailer = True
                if in_trailer:
                    trailer[i] += line
                    continue

                if line.startswith('%%Page:'):
                    pages[i] += 1

            fh.close()

            if prolog[i]:
                for j in range(i):
                    if prolog[j] == prolog[i]:
                        pages[j] += pages[i]
                        break

        largest = 0
        prolog_inx = 0
        for i, file in enumerate(args.file):
            size = len(prolog[i]) * pages[i]
            if largest < size:
                largest = size
                prolog_inx = i

    files = list(map(str, map(os.path.basename, args.file)))

    print(f'''\
%!PS-Adobe-3.0
%%Title: {' '.join(files)}
%%Creator: psjoin (from PSUtils)
%%Pages: (atend)''')
    print(comments[prolog_inx], end='')

    print(f'\n{prolog[prolog_inx]}', end='')
    for i in range(len(args.file)):
        if i in prolog and prolog[i]:
            prolog[i] = re.sub('^%%', '% %%', prolog[i], flags=re.MULTILINE)
            trailer[i] = re.sub('^%%', '% %%', trailer[i], flags=re.MULTILINE)

    total_pages = 0
    for i, file in enumerate(args.file):
        print(f'% psjoin: file: {files[i]}')
        if i not in prolog or prolog[i] != prolog[prolog_inx]:
            print('% psjoin: Prolog/Trailer will be inserted in each page')
        else:
            print('% psjoin: common Prolog/Trailer will be used')

        in_document = False
        in_comment = not args.nostrip
        in_prolog = not args.nostrip
        in_trailer = False
        saved = False
        file_pages = 0

        try:
            fh = open(file)
        except IOError as e:
            die(f"can't open file `{file[i]}': {e}")
        for line in fh:
            if line.startswith('%%BeginDocument'):
                in_document = True
            elif line.startswith('%%EndDocument'):
                in_document = False
            if in_document:
                # s/^(%[%!])/% \1/
                print(line, end='')
            else:
                if in_comment:
                    if line.startswith('%%EndComments'):
                        in_comment = False
                elif in_prolog:
                    if line.startswith('%%Page:'):
                        in_prolog = False
                    else:
                        continue
                if not args.nostrip and line.startswith('%%Trailer'):
                    in_trailer = True
                if in_trailer:
                    continue

                if line.startswith('%%Page:'):
                    if saved:
                        print(trailer[i], end='')
                        print(restore, end='')
                        saved = False

                    file_pages += 1
                    total_pages += 1
                    print(f'\n%%Page: ({i}-{file_pages}) {total_pages}')
                    if i not in prolog or prolog[i] != prolog[prolog_inx]:
                        print(save, end='')
                        if i in prolog:
                            print(prolog[i], end='')
                        saved = True
                    elif args.save:
                        print(save, end='')
                else:
                    print(re.sub(r'^(%[%!])', r'% \1', line), end='')

        fh.close()

        if args.even and file_pages % 2 != 0:
            file_pages += 1
            total_pages += 1
            print (f'''\

%%Page: ({i}-E) {total_pages}
% psjoin: empty page inserted to force even pages
showpage''')

        if i in trailer and saved:
            print(trailer[i], end='')
        if saved or args.save:
            print(restore, end='')

    print('\n%%Trailer')
    print(trailer[prolog_inx], end='')
    print(f'\n%%Pages: {total_pages}\n%%EOF', end='')

def normalize_types(types: List[str]) -> List[str]:
    normalized_types = []
    for t in types:
        if t == '.eps':
            normalized_types.append('.ps')
        else:
            normalized_types.append(t)
    return normalized_types

def psjoin(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    # Check types of files
    types = list(map(puremagic.from_file, args.file))
    types = normalize_types(types)
    if not all(t == types[0] for t in types):
        die('files are not all of the same type')

    # Process the files
    if types[0] == '.pdf':
        join_pdf(args)
    elif types[0] == '.ps':
        join_ps(args)
    else:
        die(f"unknown file type `{types[0]}'")

if __name__ == '__main__':
    psjoin()
