# Tests Makefile.am
#
# Copyright (C) Reuben Thomas 2016-2017
# See LICENSE for license

TEST_EXTENSIONS = .sh
SH_LOG_COMPILER = $(srcdir)/tests/run-test

TESTS = %D%/psbook-20.sh \
	%D%/psbook-20-signature-4.sh \
	%D%/psbook-3.sh \
	%D%/psbook-3-signature-4.sh \
	%D%/psnup-20-4.sh \
	%D%/psselect-odd.sh \
	%D%/psselect-even.sh \
	%D%/psselect-reverse.sh \
	%D%/psselect-even-reverse.sh \
	%D%/psselect-positive-range.sh \
	%D%/psselect-negative-range.sh \
	%D%/psselect-positive-negative-range.sh \
	%D%/psselect-individual-pages-and-dash-p.sh \
	%D%/psselect-options-and-complex-pagerange.sh \
	%D%/psselect-invalid-pagerange.sh

# FIXME: Write this!
#	%D%/psbook-invalid-signature-size.sh


XFAIL_TESTS = \
	%D%/psbook-invalid-signature-size.sh \
	%D%/psselect-invalid-pagerange.sh

RESULTS = \
	%D%/psbook-20-expected.ps \
	%D%/psbook-20-signature-4-expected.ps \
	%D%/psbook-3-expected.ps \
	%D%/psbook-3-signature-4-expected.ps \
	%D%/psnup-20-4-expected.ps \
	%D%/psselect-odd-expected.ps \
	%D%/psselect-even-expected.ps \
	%D%/psselect-reverse-expected.ps \
	%D%/psselect-even-reverse-expected.ps \
	%D%/psselect-positive-range-expected.ps \
	%D%/psselect-negative-range-expected.ps \
	%D%/psselect-positive-negative-range-expected.ps \
	%D%/psselect-individual-pages-and-dash-p-expected.ps \
	%D%/psselect-options-and-complex-pagerange-expected.ps

EXTRA_DIST += %D%/mktestfile $(SH_LOG_COMPILER) $(TESTS) $(RESULTS) %D%/psutils-wrapper.in

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir)/tests PATH=$(abs_top_srcdir):$(PATH) PERL5LIB=$(abs_top_srcdir)

# These files depend on Makefile so they are rebuilt if do_subst'ituted
# variables change.
tests/psutils-wrapper: tests/psutils-wrapper.in
tests/psutils-wrapper: Makefile
	$(MKDIR_P) tests
	$(AM_V_GEN)rm -f $@ $@-t \
## Common substitutions.
	  && in=$@.in && $(do_subst) <$(srcdir)/$$in >$@-t
	$(generated_file_finalize)
# FIXME: When we flatten the build system, add bin_SCRIPTS and bin_PROGRAMS as prereqs below
$(TESTS): tests/psutils-wrapper
DISTCLEANFILES += tests/psutils-wrapper

clean-local:
	rm -f $(builddir)/tests/*-input.ps $(builddir)/tests/*-output.ps
