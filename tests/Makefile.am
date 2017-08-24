# Tests Makefile.am
#
# Copyright (C) Reuben Thomas 2016
# See LICENSE for license

TEST_EXTENSIONS = .sh
SH_LOG_COMPILER = $(srcdir)/run-test

TESTS = psbook-20.sh \
	psbook-20-signature-4.sh \
	psbook-3.sh \
	psbook-3-signature-4.sh \
	psbook-invalid-signature-size.sh \
	psnup-20-4.sh \
	psselect-odd.sh \
	psselect-even.sh \
	psselect-reverse.sh \
	psselect-even-reverse.sh \
	psselect-positive-range.sh \
	psselect-negative-range.sh \
	psselect-positive-negative-range.sh \
	psselect-individual-pages-and-dash-p.sh \
	psselect-options-and-complex-pagerange.sh \
	psselect-invalid-pagerange.sh

XFAIL_TESTS = \
	psbook-invalid-signature-size.sh \
	psselect-invalid-pagerange.sh

RESULTS = \
	psbook-20-expected.ps \
	psbook-20-signature-4-expected.ps \
	psbook-3-expected.ps \
	psbook-3-signature-4-expected.ps \
	psnup-20-4-expected.ps \
	psselect-odd-expected.ps \
	psselect-even-expected.ps \
	psselect-reverse-expected.ps \
	psselect-even-reverse-expected.ps \
	psselect-positive-range-expected.ps \
	psselect-negative-range-expected.ps \
	psselect-positive-negative-range-expected.ps \
	psselect-individual-pages-and-dash-p-expected.ps \
	psselect-options-and-complex-pagerange-expected.ps

EXTRA_DIST = mktestfile run-test $(TESTS) $(RESULTS)

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir) PATH=$(top_srcdir):$(PATH) PERL5LIB=$(top_srcdir)

# FIXME: Make build system non-recursive, and remove this duplication
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
  | $(SHELL) $(top_builddir)/config.status --file=- \
  )

# These files depend on Makefile so they are rebuilt if do_subst'ituted
# variables change.
psutils-wrapper: psutils-wrapper.in
psutils-wrapper: Makefile
	$(AM_V_GEN)rm -f $@ $@-t \
## Common substitutions.
	  && in=$@.in && $(do_subst) <$(srcdir)/$$in >$@-t
	$(generated_file_finalize)
$(TESTS): psutils-wrapper

clean-local:
	rm -f *-input.ps *-output.ps
