# Makefile for PS utilities
#
# Copyright (C) Reuben Thomas 2012-2016
# See LICENSE for license

CLOC = cloc --force-lang="C",h --autoconf

SUBDIRS = lib tests

ACLOCAL_AMFLAGS = -I m4

AM_CFLAGS = $(WERROR_CFLAGS) $(WARN_CFLAGS)
AM_CPPFLAGS = $(ISYSTEM)$(top_builddir)/lib $(ISYSTEM)$(top_srcdir)/lib -DPAPER='"$(PAPER)"'
LDADD = libpsutils.a $(top_builddir)/lib/libgnu.a

noinst_LIBRARIES = libpsutils.a
libpsutils_a_SOURCES = psutil.c psspec.c
libpsutils_a_LIBADD = $(LIBPAPER)

bin_PROGRAMS = pstops epsffit psnup

bin_SCRIPTS = psbook psjoin psresize psselect extractres

SOURCES_EXTRA = psutil.h psspec.h

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

EXTRA_DIST = m4/gnulib-cache.m4 \
	LICENSE \
	$(SOURCES_EXTRA) \
	$(bin_SCRIPTS) \
	$(man_MANS)

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	$(bin_SCRIPTS) \
	$(libpsutils_a_SOURCES) \
	$(SOURCES_EXTRA) \
	$(pstops_SOURCES) $(epsffit_SOURCES) $(psnup_SOURCES)

all: includeres

loc:
	$(CLOC) $(PRODUCTIONSOURCES)

includeres: extractres
	$(RM) $@ && $(LN_S) $(srcdir)/extractres $@

install-exec-hook:
	cd $(DESTDIR)$(bindir); $(RM) includeres; $(LN_S) extractres includeres

uninstall-hook:
	$(RM) $(DESTDIR)$(bindir)/includeres

clean-local:
	$(RM) includeres
