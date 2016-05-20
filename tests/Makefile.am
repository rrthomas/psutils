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

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir) PATH=$(top_srcdir):$(PATH)

clean-local:
	rm -f *-input.ps *-output.ps
