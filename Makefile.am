# Makefile for PS utilities
#
# Copyright (C) Reuben Thomas 2012
# See LICENSE for license

SUBDIRS = lib

ACLOCAL_AMFLAGS = -I m4

noinst_LIBRARIES = libpsutils.a
libpsutils_a_SOURCES = psutil.c psspec.c pserror.c
libpsutils_a_LIBADD = $(LIBPAPER)
LDADD = libpsutils.a

bin_PROGRAMS = psbook psselect pstops epsffit psnup psresize

bin_SCRIPTS = psmerge getafm extractres includeres showchar

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psmerge.1 getafm.1 extractres.1 includeres.1 showchar.1

EXTRA_DIST = m4/gnulib-cache.m4 \
	psutil.h psspec.h pserror.h \
	$(bin_SCRIPTS) \
	$(man_MANS)
