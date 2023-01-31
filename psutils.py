# PSUtils utility library
# Copyright (c) Reuben Thomas 2023.
# Released under the GPL version 3, or (at your option) any later version.

from __future__ import annotations

import os
import sys
import argparse
import shutil
import tempfile
import subprocess
import re
import warnings
from warnings import warn
from typing import (
    Any, List, Optional, Union, Type, NoReturn,
)

import __main__

# Help output
# Adapted from https://stackoverflow.com/questions/23936145/python-argparse-help-message-disable-metavar-for-short-options
class HelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                # Option takes no argument, output: -s, --long
                parts.extend(action.option_strings)
            else:
                # Option takes an argument, output: -s, --long ARGUMENT
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)
                parts[-1] += f' {args_string}'
            # Add space at start of format string if there is no short option
            if len(action.option_strings) > 0 and action.option_strings[0][1] == '-':
                parts[-1] = '    ' + parts[-1]
            return ', '.join(parts)

# Error messages
def simple_warning( # pylint: disable=too-many-arguments
        message: Union[Warning, str],
        category: Type[Warning], # pylint: disable=unused-argument
        filename: str, # pylint: disable=unused-argument
        lineno: int, # pylint: disable=unused-argument
        file: Optional[TextIO] = sys.stderr, # pylint: disable=redefined-outer-name
        line: Optional[str] = None # pylint: disable=unused-argument
) -> None:
    print(f'\n{__main__.parser.prog}: {message}', file=file or sys.stderr)
warnings.showwarning = simple_warning

def die(msg: str, code: Optional[int] = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)

# Adapted from https://github.com/python/cpython/blob/main/Lib/test/test_strtod.py
strtod_parser = re.compile(r'''    # A numeric string consists of:
    [-+]?          # an optional sign, followed by
    (?=\d|\.\d)    # a number with at least one digit
    \d*            # having a (possibly empty) integer part
    (?:\.(\d*))?   # followed by an optional fractional part
    (?:E[-+]?\d+)? # and an optional exponent
''', re.VERBOSE | re.IGNORECASE).match

def strtod(s: str):
    m = strtod_parser(s)
    if m is None:
        raise ValueError('invalid numeric string')
    return float(m[0]), m.end()

# Argument parsers
def singledimen(s: str, width: Optional[float] = None, height: Optional[float] = None):
    num, unparsed = strtod(s)
    s = s[unparsed:]

    if s.startswith('pt'):
        pass
    elif s.startswith('in'):
        num *= 72
    elif s.startswith('cm'):
        num *= 28.346456692913385211
    elif s.startswith('mm'):
        num *= 2.8346456692913385211
    elif s.startswith('w'):
        if width is None:
            die('paper size not set')
        num *= width
    elif s.startswith('h'):
        if height is None:
            die('paper size not set')
        num *= height
    elif s != '':
        die(f"bad dimension `{s}'")

    return num

# Get the size of the given paper, or the default paper if no argument given.
def paper(cmd: List[str], silent: bool):
    cmd.insert(0, 'paper')
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL if silent else None, text=True)
        return out.rstrip()
    except subprocess.CalledProcessError:
        return None
    except:
        die("could not run `paper' command")

def paper_size(paper_name: Optional[str] = None):
    if paper_name is None:
        paper_name = paper([])
    dimensions = paper(['--unit=pt', paper_name], True)
    if dimensions is None:
        return None, None
    m = re.search(' ([.0-9]+)x([.0-9]+) pt$', dimensions)
    w, h = float(m[1]), float(m[2])
    return int(w + 0.5), int(h + 0.5) # round dimensions to nearest point

def parsepaper(paper: str):
    try:
        (width, height) = paper_size(paper)
        if width is None:
            [width, height] = paper.split('x')
            if width and height:
                width, height = singledimen(width), singledimen(height)
        return width, height
    except:
        die(f"paper size '{paper}' unknown")

def parse_input_paper(s: str):
  __main__.iwidth, __main__.iheight = parsepaper(s)

def parse_output_paper(s: str):
  __main__.width, __main__.height = parsepaper(s)

def parsedimen(s: str):
    return singledimen(s, __main__.width, __main__.height)

def parsedraw(s: str):
    return parsedimen(s or '1')

# Return comment keyword and value if `line' is a DSC comment
def comment(line: str) -> Optional[(str, str)]:
    m = re.match(r'%%(\S+)\s+?(.*\S?)\s*$', line)
    if m:
        return m[1], m[2]

# Build array of pointers to start/end of pages
def parse_file(infile: IO, explicit_output_paper: bool = False):
    nesting = 0
    psinfo = {
        'headerpos': 0,
        'pagescmt': 0,
        'endsetup': 0,
        'beginprocset': 0,          # start and end of pstops procset
        'endprocset': 0,
        'pages': None,
        'sizeheaders': [],
        'pageptr': [],
    }
    infile.seek(0)
    record, next_record, buffer = 0, 0, None
    for buffer in infile:
        next_record += len(buffer)
        if buffer.startswith('%%'):
            keyword, value = comment(buffer)
            if keyword is not None:
                if nesting == 0 and keyword == 'Page:':
                    psinfo['pageptr'].append(record)
                elif psinfo['headerpos'] == 0 and explicit_output_paper and \
                    keyword in ['BoundingBox:', 'HiResBoundingBox:', 'DocumentPaperSizes:', 'DocumentMedia:']:
                    # FIXME: read input paper size (from DocumentMedia comment?) if not
                    # set on command line.
                    psinfo['sizeheaders'].append(record)
                elif psinfo['headerpos'] == 0 and keyword == 'Pages:':
                    psinfo['pagescmt'] = record
                elif psinfo['headerpos'] == 0 and keyword == 'EndComments':
                    psinfo['headerpos'] = next_record
                elif keyword in ['BeginDocument:', 'BeginBinary:', 'BeginFile:']:
                    nesting += 1
                elif keyword in ['EndDocument', 'EndBinary', 'EndFile']:
                    nesting -= 1
                elif nesting == 0 and keyword == 'EndSetup':
                    psinfo['endsetup'] = record
                elif nesting == 0 and keyword == 'BeginProlog':
                    psinfo['headerpos'] = next_record
                elif nesting == 0 and buffer == '%%BeginProcSet: PStoPS':
                    psinfo['beginprocset'] = record
                elif psinfo['beginprocset'] is not None and \
                     psinfo['endprocset'] is None and keyword == 'EndProcSet':
                    psinfo['endprocset'] = next_record
                elif nesting == 0 and keyword in ['Trailer', 'EOF']:
                    break
        elif psinfo['headerpos'] == 0:
            psinfo['headerpos'] = record
        record = next_record
    psinfo['pages'] = len(psinfo['pageptr'])
    psinfo['pageptr'].append(record)
    if psinfo['endsetup'] == 0 or psinfo['endsetup'] > psinfo['pageptr'][0]:
        psinfo['endsetup'] = psinfo['pageptr'][0]
    return psinfo

# Set up input and output files
def setup_input_and_output(infile_name: str, outfile_name: str, make_seekable: bool = False) -> (IO, IO):
    if infile_name is not None:
        try:
            infile = open(infile_name)
        except:
            die(f'cannot open input file {infile_name}')
    else:
        infile = sys.stdin
    infile.reconfigure(newline=None)
    if make_seekable:
        infile = seekable(infile)
    if infile is None:
        die('cannot make input seekable')

    if outfile_name is not None:
        try:
            outfile = open(outfile_name, 'w')
        except:
            die(f'cannot open output file {outfile_name}')
    else:
        outfile = sys.stdout
    outfile.reconfigure(newline=None)

    return infile, outfile

# Make a file handle seekable, using a temporary file if necessary
def seekable(fp: IO) -> Optional[IO]:
    if fp.seekable():
        return fp

    try:
        ft = tempfile.TemporaryFile()
        shutil.copyfileobj(fp, ft)
        ft.seek(0)
        return ft
    except IOError:
        return None

# Resource extensions
def extn(ext):
    exts = {'font': '.pfa', 'file': '.ps', 'procset': '.ps',
            'pattern': '.pat', 'form': '.frm', 'encoding': '.enc'}
    return exts.get(ext, '')

# Resource filename
def filename(*components): # make filename for resource in 'components'
    name = ''
    for c in components: # sanitise name
        c = re.sub(r'[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]', '', c)
        name += c
    name = os.path.basename(name) # drop directories
    if name == '':
        die(f'filename not found for resource {" ".join(components)}', 2)
    return name
