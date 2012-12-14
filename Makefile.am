# Makefile for PS utilities
#
# Copyright (C) Reuben Thomas 2012
# See LICENSE for license

SUBDIRS = lib

ACLOCAL_AMFLAGS = -I m4

noinst_LIBRARIES = libpsutils.a
libpsutils_a_SOURCES = psutil.c psspec.c pserror.c
libpsutils_a_LIBADD = $(LIBPAPER)

bin_PROGRAMS = psbook psselect pstops epsffit psnup psresize

bin_SCRIPTS = getafm showchar \
	fixfmps fixpsditps fixpspps \
	fixtpps fixwfwps fixwpps fixscribeps fixwwps \
	fixdlsrps extractres includeres psmerge

EXTRA_DIST = m4/gnulib-cache.m4 \
	psutil.h psspec.h pserror.h \
	maketext \
	includeres.in \
	epsffit.man extractres.man fixdlsrps.man fixfmps.man \
	fixpsditps.man fixpspps.man fixscribeps.man fixtpps.man \
	fixwfwps.man fixwpps.man fixwwps.man getafm.man \
	includeres.man.in psbook.man psmerge.man psnup.man \
	psresize.man psselect.man pstops.man showchar.man \
	$(bin_SCRIPTS)

man_MANS = psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 \
	psresize.1 psmerge.1 fixscribeps.1 getafm.1 \
	fixdlsrps.1 fixfmps.1 fixpsditps.1 \
	fixpspps.1 fixtpps.1 fixwfwps.1 fixwpps.1 \
	fixwwps.1 extractres.1 includeres.1 \
	showchar.1

automake_edit = sed \
	-e 's|@pkgdatadir[@]|$(pkgdatadir)|g'

$(top_builddir)/includeres: Makefile includeres.in
	rm -f $@ $@.tmp
	$(automake_edit) '$(top_srcdir)/$@.in' >$@.tmp
	mv $@.tmp $@
	chmod +x $@

$(top_builddir)/includeres.man: Makefile includeres.man.in
	rm -f $@ $@.tmp
	$(automake_edit) '$(top_srcdir)/$@.in' >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(man_MANS)

DISTCLEANFILES = includeres includeres.man

LDADD = libpsutils.a

.man.1:
	$(PERL) $(srcdir)/maketext VERSION=$(PACKAGE_VERSION) MAN="$(man_MANS)" $? > $@
