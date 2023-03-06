# Makefile.am for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2023
# See COPYING for license

ACLOCAL_AMFLAGS = -I m4

CLOC = cloc --autoconf

bin_SCRIPTS = pstops psbook psjoin psresize psselect psnup epsffit extractres includeres

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

EXTRA_DIST = \
	COPYING \
	psutils.py \
	$(man_MANS)

DISTCLEANFILES = $(bin_SCRIPTS)

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	psutils.py \
	$(bin_SCRIPTS)

install-exec-hook:
	if test "x$(EXEEXT)" != "x"; then \
	  for script in $(bin_SCRIPTS); do \
	    mv $(DESTDIR)$(bindir)/$$script $(DESTDIR)$(bindir)/$$script$(PERL_EXEEXT); \
	  done; \
	fi

%.1: % %-include.man man-include.man
## Exit gracefully if $@ is not writeable, such as during distcheck!
	$(AM_V_GEN)if ( touch $@.w && rm -f $@.w; ) >/dev/null 2>&1; then \
	  $(top_builddir)/pre-inst-env $(top_srcdir)/build-aux/missing --run $(HELP2MAN) --no-info \
		--no-discard-stderr \
		--include=$(srcdir)/$*-include.man \
		--include=$(srcdir)/man-include.man \
		--output=$@ ./$*; \
	fi

include tests/Makefile.am

loc:
	$(CLOC) $(PRODUCTIONSOURCES)

release: distcheck
	git diff --exit-code && \
	git tag -a -m "Release tag" "v$(VERSION)" && \
	git push && git push --tags && \
	woger github package=$(PACKAGE) version=$(VERSION) dist_type=tar.gz
