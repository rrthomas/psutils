# Makefile.am for PSUtils

CLOC = cloc --force-lang="C",h --autoconf

SUBDIRS = lib tests

ACLOCAL_AMFLAGS = -I m4

AM_CFLAGS = $(WERROR_CFLAGS) $(WARN_CFLAGS)
AM_CPPFLAGS = $(ISYSTEM)$(top_builddir)/lib $(ISYSTEM)$(top_srcdir)/lib -DPAPER='"$(PAPER)"'
LDADD = $(top_builddir)/lib/libgnu.a

bin_PROGRAMS = pstops

bin_SCRIPTS = psbook psjoin psresize psselect psnup epsffit extractres

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

EXTRA_DIST = m4/gnulib-cache.m4 \
	COPYING \
	$(bin_SCRIPTS) \
	$(man_MANS)

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	$(bin_SCRIPTS) \
	$(pstops_SOURCES)

all: includeres

loc:
	$(CLOC) $(PRODUCTIONSOURCES)

includeres: extractres
	rm -f $@ && $(LN_S) $(srcdir)/extractres $@

install-exec-hook:
	cd $(DESTDIR)$(bindir); rm -f includeres; $(LN_S) extractres includeres

uninstall-hook:
	rm -f $(DESTDIR)$(bindir)/includeres

clean-local:
	rm -f includeres
