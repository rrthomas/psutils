# PostScript Utilities

Web site: https://github.com/rrthomas/psutils
Maintainer: Reuben Thomas <rrt@sc3d.org>

PSUtils is a suite of utilities for manipulating PostScript documents
produced according to the Document Structuring Conventions. You can select
and rearrange pages, including arrangement into signatures for booklet
printing, combine multple pages into a single page for n-up printing, and
resize, flip and rotate pages.

PSUtils is distributed under the GNU General Public License version 3, or,
at your option, any later version; see the file COPYING. (Some of the input
files in the tests directory are not under this license; see the file
COPYRIGHT in that directory.)

If you simply want to use PSUtils, you will find it in most GNU/Linux
distributions; it is available in brew for macOS and Cygwin for Windows.

The PSUtils utilities intentionally do not check their input is
DSC-conformant, as some programs produce non-conforming output that can be
successfully processed anyway. If PSUtils does not work for you, check
whether your software needs to be configured to produce DSC-conformant
PostScript.


## Prerequisites

PSUtils requires Python 3, and libpaper, which allows named paper sizes to be
used and configured:

libpaper: https://github.com/rrthomas/libpaper


## Installation from source

You need a standard POSIX environment.

Having unpacked the source tarball, run:

```
./configure && make check && [sudo] make install
```

For build options, see ./configure --help

Note that to use the scripts before installing them, you need to run them
as Python modules; for example:

```
python -m psutils.psnup -2 foo.ps
```

## Installation from git

To build from git, you need the following extra programs installed:

  automake, autoconf, git

Then run:

```
./bootstrap
```

Now follow the normal installation instructions above.


## Bugs

Please send bug reports, patches and suggestions to the bug tracker or
maintainer (see the top of this file).


## Acknowledgements

PSUtils is written and maintained by Reuben Thomas. Version 1 was written by
Angus Duggan.

psselect in modeled on Chris Torek's dviselect, as is psbook, via Angus
Duggan's dvibook; pstops is modeled on Tom Rokicki's dvidvi. psjoin was
originally written by Tom Sato.
