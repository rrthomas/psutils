# Tests Makefile.am
#
# Copyright (C) Reuben Thomas 2016
# See LICENSE for license

TESTS = psbook-test \
	psselect-test

RESULTS = psbook-expected.ps \
	psselect-expected.ps

EXTRA_DIST = mktestfile $(TESTS) $(RESULTS)

AM_TESTS_ENVIRONMENT = srcdir=$(srcdir) top_srcdir=$(top_srcdir)

clean-local:
	rm -f *-test.ps
