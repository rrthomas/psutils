# Makefile.am for PSUtils
#
# Copyright (C) Reuben Thomas 2016-2017
# See LICENSE for license

CLOC = cloc --force-lang="C",h --autoconf

SUBDIRS = lib .

ACLOCAL_AMFLAGS = -I m4

AM_CFLAGS = $(WERROR_CFLAGS) $(WARN_CFLAGS)
AM_CPPFLAGS = $(ISYSTEM)$(top_builddir)/lib $(ISYSTEM)$(top_srcdir)/lib -DPAPER='"$(PAPER)"'
LDADD = $(top_builddir)/lib/libgnu.a

bin_PROGRAMS = pstops
bin_SCRIPTS = psbook psjoin psresize psselect psnup epsffit extractres
dist_pkgdata_DATA = PSUtils.pm

# Generated files shouldn't contain unexpanded '@substitutions@', and
# should be made read-only, to prevent them from being edited by mistake
# instead of the file they are generated from.
generated_file_finalize = $(AM_V_at) \
  if LC_ALL=C grep '@[a-zA-Z0-9_][a-zA-Z0-9_]*@' $@-t; then \
    echo "$@ contains unexpanded substitution (see lines above)"; \
    exit 1; \
  fi; \
  chmod a+x,a-w $@-t && mv -f $@-t $@

# We want a handful of substitutions to be fully-expanded by make;
# then use config.status to substitute the remainder where a single
# expansion is sufficient.  We use a funny notation here to avoid
# configure substitutions in our text.
do_subst = ( sed \
  -e "s,[@]configure_input[@],Generated from $$in; do not edit by hand.,g" \
  -e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
  | $(SHELL) ./config.status --file=- \
  )

# These files depend on Makefile so they are rebuilt if do_subst'ituted
# variables change.
psbook: psbook.in
psjoin: psjoin.in
psresize: psresize.in
psselect: psselect.in
psnup: psnup.in
epsffit: epsffit.in
psbook psjoin psresize psselect psnup epsffit: Makefile
	$(AM_V_GEN)rm -f $@ $@-t \
## Common substitutions.
	  && in=$@.in && $(do_subst) <$(srcdir)/$$in >$@-t
	$(generated_file_finalize)

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

EXTRA_DIST = m4/gnulib-cache.m4 \
	COPYING \
	extractres \
	psbook.in psjoin.in psresize.in psselect.in psnup.in epsffit.in \
	$(man_MANS)

DISTCLEANFILES = psbook psjoin psresize psselect psnup epsffit

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	$(bin_SCRIPTS) \
	$(pstops_SOURCES)

include tests/Makefile.am

all: includeres

loc:
	$(CLOC) $(PRODUCTIONSOURCES)

includeres: extractres
	rm -f $@ && $(LN_S) $(srcdir)/extractres $@

install-exec-hook:
	cd $(DESTDIR)$(bindir); rm -f includeres; $(LN_S) extractres includeres

uninstall-hook:
	rm -f $(DESTDIR)$(bindir)/includeres

CLEANFILES = includeres
