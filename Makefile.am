# Makefile.am for PSUtils
#
# Copyright (C) Reuben Thomas 2012-2020
# See COPYING for license

ACLOCAL_AMFLAGS = -I m4

CLOC = cloc --autoconf

bin_SCRIPTS = pstops psbook psjoin psresize psselect psnup epsffit extractres includeres
dist_pkgdata_DATA = PSUtils.pm

man_MANS = psutils.1 \
	psbook.1 psselect.1 pstops.1 epsffit.1 psnup.1 psresize.1 \
	psjoin.1 extractres.1 includeres.1

# Generated files shouldn't contain unexpanded '@substitutions@', and
# should be made read-only, to prevent them from being edited by mistake
# instead of the file they are generated from.
generated_file_finalize = $(AM_V_at) \
  if LC_ALL=C grep '^[^\#].*@[a-zA-Z0-9_][a-zA-Z0-9_]*@' $@-t; then \
    echo "$@ contains unexpanded substitution (see lines above)"; \
    exit 1; \
  fi; \
  chmod a+x,a-w $@-t && mv -f $@-t $@

# We want a handful of substitutions to be fully-expanded by make;
# then use config.status to substitute the remainder where a single
# expansion is sufficient.  We use a funny notation here to avoid
# configure substitutions in our text.
do_subst = ( sed \
  -e 's|$$[{]prefix[}]|$(prefix)|g' \
  -e 's|$$[{]exec_prefix[}]|$(exec_prefix)|g' \
  -e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
  | $(SHELL) ./config.status --file=- \
  )

# These files depend on Makefile so they are rebuilt if do_subst'ituted
# variables change.
pstops: pstops.in
psbook: psbook.in
psjoin: psjoin.in
psresize: psresize.in
psselect: psselect.in
psnup: psnup.in
epsffit: epsffit.in
extractres: extractres.in
includeres: includeres.in
pstops psbook psjoin psresize psselect psnup epsffit extractres includeres: Makefile
	$(AM_V_GEN)rm -f $@ $@-t \
## Common substitutions.
	 && in=$(builddir)/$@.in && $(do_subst) <$$in >$@-t
	$(generated_file_finalize)

EXTRA_DIST = \
	COPYING \
	PSUtils.pm \
	$(man_MANS)

DISTCLEANFILES = $(bin_SCRIPTS)

PRODUCTIONSOURCES = \
	configure.ac \
	Makefile.am \
	PSUtils.pm \
	$(bin_SCRIPTS)

install-exec-hook:
	if test "x$(EXEEXT)" != "x"; then \
	  mv $(DESTDIR)$(bindir)/paper $(DESTDIR)$(bindir)/paper$(PERL_EXEEXT); \
	fi

%.1: % %-include.man man-include.man
## Exit gracefully if $@ is not writeable, such as during distcheck!
	$(AM_V_GEN)if ( touch $@.w && rm -f $@.w; ) >/dev/null 2>&1; then \
	  $(srcdir)/pre-inst-env $(top_srcdir)/build-aux/missing --run $(HELP2MAN) --no-info \
		--include=$(srcdir)/man-include.man \
		--include=$(srcdir)/$*-include.man \
		--output=$@ ./$*; \
	fi

include tests/Makefile.am

loc:
	$(CLOC) $(PRODUCTIONSOURCES)
	echo "Subtract 9 times the following total:"
	$(CLOC) --force-lang=perl build-aux/relocatable.pl.in

release: distcheck
	git diff --exit-code && \
	git tag -a -m "Release tag" "v$(VERSION)" && \
	git push && git push --tags && \
	woger github \
		github_user=rrthomas \
		package=psutils \
		version=$(VERSION) \
		dist_type=tar.gz
