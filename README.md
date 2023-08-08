# PDF and PostScript Utilities

Web site: https://github.com/rrthomas/psutils  
Maintainer: Reuben Thomas <rrt@sc3d.org>  

PSUtils is a suite of utilities for manipulating PDF and PostScript
documents. You can select and rearrange pages, including arrangement into
signatures for booklet printing, combine multple pages into a single page
for n-up printing, and resize, flip and rotate pages.

PSUtils is distributed under the GNU General Public License version 3, or,
at your option, any later version; see the file COPYING. (Some of the input
files in the tests directory are not under this license; see the file
COPYRIGHT in that directory.)

If you simply want to use PSUtils, you will find it in most GNU/Linux
distributions; it is available in brew for macOS and Cygwin for Windows.

PostScript files should conform to the PostScript Document Structuring
Conventions (DSC); however, PSUtils intentionally does not check this, as
some programs produce non-conforming output that can be successfully
processed anyway. If PSUtils does not work for you, check whether your
software needs to be configured to produce DSC-conformant PostScript.

Some old Perl scripts, which mostly fix up the output of various obsolete
programs and drivers to enable PSUtils to process it, are available in git
in the `old-scripts` directory. They are not supported, and their use is
discouraged, unless you know you need them!


## Installation

The easiest way to install PSUtils is from PyPI, the Python Package Index:

`pip install pspdfutils`

(Note the PyPI package name!)


## Installation from source or git

PSUtils requires Python 3.9 or later, a handful of Python libraries (listed
in `pyproject.toml`, and automatically installed by the build procedure),
and libpaper, which allows named paper sizes to be used and configured:

libpaper: https://github.com/rrthomas/libpaper

In the source directory: `python -m build` (requires the `build` package to
be installed).

Note that to use the scripts before installing them, you need to run them
as Python modules; for example:

```
PYTHONPATH=. python -m psutils.command.psnup -2 foo.ps
```


## Bugs

Please send bug reports, patches and suggestions to the bug tracker or
maintainer (see the top of this file).


## Acknowledgements

PSUtils is written and maintained by Reuben Thomas. Version 1 was written by
Angus Duggan.

psselect in modeled on Chris Torek's dviselect, as is psbook, via Angus
Duggan's dvibook; pstops is modeled on Tom Rokicki's dvidvi. psjoin was
originally written by Tom Sato.
