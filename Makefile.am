# Makefile.am for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2019
# See COPYING for license

CLOC = cloc --autoconf

bin_SCRIPTS = pstops psbook psjoin psresize psselect psnup epsffit extractres includeres
perldir = $(datadir)/perl
perl_DATA = PSUtils.pm

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

EXTRA_DIST = \
	COPYING \
	pstops.in psbook.in psjoin.in psresize.in psselect.in psnup.in epsffit.in extractres.in includeres.in \
	$(man_MANS)

DISTCLEANFILES = $(bin_SCRIPTS)

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	$(bin_SCRIPTS)

include tests/Makefile.am

loc:
	$(CLOC) $(PRODUCTIONSOURCES)
